#!/usr/bin/env python3
"""
Low-Resource AI Researcher - Medical PEFT Trainer
基于PEFT技术的医疗模型微调工具

Author: OpenClaw Skill
Version: 1.0.0
"""

import os
import json
import logging
import argparse
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# Transformers
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    DataCollatorForSeq2Seq,
    BitsAndBytesConfig,
    EarlyStoppingCallback,
    get_linear_schedule_with_warmup,
)
from transformers.integrations import WandbCallback

# PEFT
from peft import (
    LoraConfig,
    PeftModel,
    PeftConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
    set_peft_model_state_dict,
)

# Datasets
from datasets import load_dataset, Dataset, DatasetDict

# Accelerate
from accelerate import Accelerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MedicalTrainingConfig:
    """医疗模型训练配置"""
    # Model config
    model_name_or_path: str = "meta-llama/Llama-2-7b-hf"
    tokenizer_name: Optional[str] = None
    trust_remote_code: bool = True
    
    # LoRA config
    use_lora: bool = True
    use_qlora: bool = False
    lora_r: int = 64
    lora_alpha: int = 128
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "v_proj", "k_proj", "o_proj", 
        "gate_proj", "up_proj", "down_proj"
    ])
    
    # Quantization config
    load_in_4bit: bool = False
    load_in_8bit: bool = False
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_use_double_quant: bool = True
    bnb_4bit_quant_type: str = "nf4"
    
    # Training config
    output_dir: str = "./output"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.001
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    max_grad_norm: float = 0.3
    
    # Data config
    max_seq_length: int = 2048
    dataset_name: str = "medical_qa"
    dataset_config: Optional[str] = None
    train_file: Optional[str] = None
    validation_file: Optional[str] = None
    template: str = "medical_chat"
    
    # Optimization
    fp16: bool = False
    bf16: bool = True
    gradient_checkpointing: bool = True
    group_by_length: bool = True
    
    # Logging
    logging_steps: int = 10
    eval_steps: int = 100
    save_steps: int = 500
    save_total_limit: int = 3
    
    # Other
    seed: int = 42
    dataloader_num_workers: int = 4
    remove_unused_columns: bool = False
    report_to: str = "none"  # wandb, tensorboard, none


class MedicalDataProcessor:
    """医疗数据处理器"""
    
    MEDICAL_TEMPLATES = {
        "medical_chat": {
            "system": "You are a helpful medical assistant. Provide accurate, evidence-based medical information.",
            "prompt": "### Question:\n{question}\n\n### Answer:\n{answer}",
        },
        "clinical_note": {
            "system": "You are a clinical documentation assistant. Generate accurate clinical notes.",
            "prompt": "### Patient Information:\n{patient_info}\n\n### Clinical Note:\n{note}",
        },
        "diagnosis": {
            "system": "You are a diagnostic assistant. Provide differential diagnoses based on symptoms.",
            "prompt": "### Symptoms:\n{symptoms}\n\n### Diagnosis:\n{diagnosis}",
        },
    }
    
    def __init__(self, tokenizer, config: MedicalTrainingConfig):
        self.tokenizer = tokenizer
        self.config = config
        self.template = self.MEDICAL_TEMPLATES.get(config.template, self.MEDICAL_TEMPLATES["medical_chat"])
        
    def load_medical_dataset(self) -> DatasetDict:
        """加载医疗数据集"""
        dataset_name = self.config.dataset_name
        
        # 内置医疗数据集映射
        dataset_map = {
            "pubmedqa": ("pubmed_qa", "pqa_labeled"),
            "medqa": ("bigbio/med_qa", None),
            "medmcqa": ("medmcqa", None),
            "medical_qa": ("lavita/medical-qa-datasets", None),
        }
        
        if dataset_name in dataset_map:
            name, config = dataset_map[dataset_name]
            try:
                dataset = load_dataset(name, config)
                return self._process_builtin_dataset(dataset, dataset_name)
            except Exception as e:
                logger.warning(f"Failed to load {dataset_name}: {e}. Using mock dataset.")
                return self._create_mock_dataset()
        
        # 从文件加载
        if self.config.train_file:
            data_files = {"train": self.config.train_file}
            if self.config.validation_file:
                data_files["validation"] = self.config.validation_file
            return load_dataset("json", data_files=data_files)
        
        # 默认使用mock数据
        return self._create_mock_dataset()
    
    def _process_builtin_dataset(self, dataset: DatasetDict, name: str) -> DatasetDict:
        """处理内置数据集格式"""
        def format_pubmedqa(example):
            return {
                "instruction": example.get("question", ""),
                "input": "",
                "output": example.get("long_answer", example.get("final_decision", ""))
            }
        
        def format_medqa(example):
            return {
                "instruction": example.get("question", ""),
                "input": "",
                "output": example.get("answer", "")
            }
        
        format_func = {
            "pubmedqa": format_pubmedqa,
            "medqa": format_medqa,
        }.get(name, format_medqa)
        
        processed = {}
        for split in dataset.keys():
            processed[split] = dataset[split].map(format_func, remove_columns=dataset[split].column_names)
        
        return DatasetDict(processed)
    
    def _create_mock_dataset(self) -> DatasetDict:
        """创建示例医疗数据集用于测试"""
        mock_data = [
            {
                "instruction": "What are the common symptoms of type 2 diabetes?",
                "input": "",
                "output": "Common symptoms of type 2 diabetes include increased thirst, frequent urination, extreme hunger, unexplained weight loss, fatigue, blurred vision, slow-healing sores, and frequent infections."
            },
            {
                "instruction": "Explain the mechanism of action of ACE inhibitors.",
                "input": "",
                "output": "ACE inhibitors work by blocking the angiotensin-converting enzyme (ACE), which prevents the conversion of angiotensin I to angiotensin II. This results in vasodilation, reduced aldosterone secretion, and decreased blood pressure."
            },
            {
                "instruction": "What are the contraindications for aspirin?",
                "input": "",
                "output": "Contraindications for aspirin include allergy to NSAIDs, history of asthma induced by aspirin, bleeding disorders, active peptic ulcer disease, severe hepatic or renal impairment, and children with viral infections."
            },
        ]
        return DatasetDict({
            "train": Dataset.from_list(mock_data * 100),
            "validation": Dataset.from_list(mock_data[:3])
        })
    
    def preprocess_function(self, examples: Dict[str, List]) -> Dict[str, List]:
        """预处理函数 - 格式化对话"""
        instructions = examples.get("instruction", [])
        inputs = examples.get("input", [])
        outputs = examples.get("output", [])
        
        texts = []
        for instruction, input_text, output in zip(instructions, inputs, outputs):
            if input_text:
                question = f"{instruction}\n{input_text}"
            else:
                question = instruction
            
            text = self.template["prompt"].format(
                question=question,
                answer=output
            )
            texts.append(text)
        
        # Tokenize
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            max_length=self.config.max_seq_length,
            padding="max_length",
            return_tensors=None,
        )
        
        # For causal LM, labels = input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized


class MedicalPEFTTrainer:
    """
    医疗领域PEFT训练器
    
    支持LoRA/QLoRA在消费级GPU或A100上高效微调医疗大模型
    """
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        task: str = "medical_qa",
        lora_r: int = 64,
        lora_alpha: int = 128,
        use_qlora: bool = False,
        target_modules: Optional[List[str]] = None,
        device_map: str = "auto",
        trust_remote_code: bool = True,
        config: Optional[MedicalTrainingConfig] = None
    ):
        """
        初始化医疗PEFT训练器
        
        Args:
            model_name: 基础模型名称或路径
            task: 任务类型 - medical_qa, diagnosis, clinical_note
            lora_r: LoRA rank
            lora_alpha: LoRA scaling factor
            use_qlora: 是否使用4-bit量化QLoRA
            target_modules: LoRA目标模块列表
            device_map: 设备映射策略
            trust_remote_code: 是否信任远程代码
            config: 完整训练配置
        """
        self.config = config or MedicalTrainingConfig()
        
        # Override config with direct parameters
        self.config.model_name_or_path = model_name
        self.config.lora_r = lora_r
        self.config.lora_alpha = lora_alpha
        self.config.use_qlora = use_qlora
        self.config.load_in_4bit = use_qlora
        self.config.trust_remote_code = trust_remote_code
        
        if target_modules:
            self.config.lora_target_modules = target_modules
        
        self.model = None
        self.tokenizer = None
        self.peft_config = None
        self.data_processor = None
        
        logger.info(f"Initializing MedicalPEFTTrainer with model: {model_name}")
        logger.info(f"Task: {task}, QLoRA: {use_qlora}")
    
    def _setup_quantization_config(self) -> Optional[BitsAndBytesConfig]:
        """配置量化参数"""
        if not (self.config.load_in_4bit or self.config.load_in_8bit):
            return None
        
        if self.config.load_in_4bit:
            logger.info("Using 4-bit quantization (QLoRA)")
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=getattr(torch, self.config.bnb_4bit_compute_dtype),
                bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
                bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
            )
        else:
            logger.info("Using 8-bit quantization")
            return BitsAndBytesConfig(load_in_8bit=True)
    
    def load_model_and_tokenizer(self):
        """加载模型和分词器"""
        logger.info(f"Loading model: {self.config.model_name_or_path}")
        
        # Quantization config
        quantization_config = self._setup_quantization_config()
        
        # Load tokenizer
        tokenizer_name = self.config.tokenizer_name or self.config.model_name_or_path
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name,
            trust_remote_code=self.config.trust_remote_code,
            padding_side="right",
        )
        
        # Set pad token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name_or_path,
            quantization_config=quantization_config,
            device_map=self.config.device_map if quantization_config else None,
            trust_remote_code=self.config.trust_remote_code,
            torch_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
            attn_implementation="flash_attention_2" if self._check_flash_attn() else "eager",
        )
        
        # Enable gradient checkpointing for memory efficiency
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
        
        logger.info(f"Model loaded. Parameters: {self.model.num_parameters():,}")
        
        # Prepare model for k-bit training if quantized
        if quantization_config:
            self.model = prepare_model_for_kbit_training(self.model)
        
        # Setup LoRA
        if self.config.use_lora:
            self._setup_lora()
    
    def _check_flash_attn(self) -> bool:
        """检查是否可以使用Flash Attention"""
        try:
            import flash_attn
            return True
        except ImportError:
            return False
    
    def _setup_lora(self):
        """配置LoRA"""
        self.peft_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias=self.config.bias if hasattr(self.config, 'bias') else "none",
            task_type=TaskType.CAUSAL_LM,
        )
        
        self.model = get_peft_model(self.model, self.peft_config)
        self.model.print_trainable_parameters()
        
        logger.info(f"LoRA config - r: {self.config.lora_r}, alpha: {self.config.lora_alpha}")
        logger.info(f"Target modules: {self.config.lora_target_modules}")
    
    def train(
        self,
        output_dir: Optional[str] = None,
        num_epochs: Optional[int] = None,
        batch_size: Optional[int] = None,
        gradient_accumulation_steps: Optional[int] = None,
        learning_rate: Optional[float] = None,
        **kwargs
    ):
        """
        开始训练
        
        Args:
            output_dir: 输出目录
            num_epochs: 训练轮数
            batch_size: 批次大小
            gradient_accumulation_steps: 梯度累积步数
            learning_rate: 学习率
            **kwargs: 其他训练参数
        """
        # Update config
        if output_dir:
            self.config.output_dir = output_dir
        if num_epochs:
            self.config.num_train_epochs = num_epochs
        if batch_size:
            self.config.per_device_train_batch_size = batch_size
        if gradient_accumulation_steps:
            self.config.gradient_accumulation_steps = gradient_accumulation_steps
        if learning_rate:
            self.config.learning_rate = learning_rate
        
        # Load model if not loaded
        if self.model is None:
            self.load_model_and_tokenizer()
        
        # Setup data processor
        self.data_processor = MedicalDataProcessor(self.tokenizer, self.config)
        
        # Load dataset
        logger.info("Loading dataset...")
        dataset = self.data_processor.load_medical_dataset()
        
        # Preprocess
        logger.info("Preprocessing dataset...")
        processed_dataset = dataset.map(
            self.data_processor.preprocess_function,
            batched=True,
            remove_columns=dataset["train"].column_names,
            desc="Processing dataset"
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            warmup_ratio=self.config.warmup_ratio,
            lr_scheduler_type=self.config.lr_scheduler_type,
            max_grad_norm=self.config.max_grad_norm,
            logging_steps=self.config.logging_steps,
            eval_strategy="steps" if "validation" in processed_dataset else "no",
            eval_steps=self.config.eval_steps if "validation" in processed_dataset else None,
            save_strategy="steps",
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            gradient_checkpointing=self.config.gradient_checkpointing,
            group_by_length=self.config.group_by_length,
            report_to=self.config.report_to,
            remove_unused_columns=self.config.remove_unused_columns,
            seed=self.config.seed,
            load_best_model_at_end=True if "validation" in processed_dataset else False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=processed_dataset["train"],
            eval_dataset=processed_dataset.get("validation"),
            data_collator=data_collator,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)] if "validation" in processed_dataset else None,
        )
        
        # Train
        logger.info("Starting training...")
        trainer.train()
        
        # Save
        logger.info(f"Saving model to {self.config.output_dir}")
        trainer.save_model(self.config.output_dir)
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        # Save config
        with open(os.path.join(self.config.output_dir, "training_config.json"), "w") as f:
            json.dump(self.config.__dict__, f, indent=2, default=str)
        
        logger.info("Training completed!")
        return trainer
    
    def evaluate(self, eval_dataset: Optional[Dataset] = None) -> Dict[str, float]:
        """评估模型"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model_and_tokenizer() first.")
        
        # TODO: Implement medical-specific evaluation metrics
        # - MedQA accuracy
        # - PubMedQA performance
        # - Clinical coherence scoring
        
        logger.info("Evaluation completed")
        return {}
    
    def merge_and_save(self, output_path: str):
        """
        合并LoRA权重并保存完整模型
        
        Args:
            output_path: 输出路径
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        logger.info(f"Merging LoRA weights and saving to {output_path}")
        
        # Merge
        merged_model = self.model.merge_and_unload()
        
        # Save
        merged_model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        
        logger.info("Merged model saved")
    
    def load_model(self, model_path: str):
        """加载已训练的模型"""
        logger.info(f"Loading model from {model_path}")
        
        # Check if it's a PEFT model
        if os.path.exists(os.path.join(model_path, "adapter_config.json")):
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name_or_path,
                torch_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
                device_map="auto",
            )
            # Load adapter
            self.model = PeftModel.from_pretrained(base_model, model_path)
        else:
            # Load as regular model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
                device_map="auto",
            )
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        logger.info("Model loaded successfully")
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        **kwargs
    ) -> str:
        """
        生成医疗文本回复
        
        Args:
            prompt: 输入提示
            max_new_tokens: 最大生成token数
            temperature: 采样温度
            top_p: nucleus sampling参数
            top_k: top-k sampling参数
            **kwargs: 其他生成参数
        
        Returns:
            生成的文本
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model_and_tokenizer() first.")
        
        self.model.eval()
        
        # Format prompt
        template = MedicalDataProcessor.MEDICAL_TEMPLATES["medical_chat"]
        formatted_prompt = template["prompt"].format(
            question=prompt,
            answer=""
        )
        
        # Tokenize
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response part
        if "### Answer:" in generated_text:
            generated_text = generated_text.split("### Answer:")[-1].strip()
        
        return generated_text


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Medical PEFT Trainer")
    
    # Model arguments
    parser.add_argument("--model_name_or_path", type=str, required=True,
                        help="Path to pretrained model or model identifier")
    parser.add_argument("--tokenizer_name", type=str, default=None,
                        help="Pretrained tokenizer name or path")
    
    # LoRA arguments
    parser.add_argument("--use_lora", action="store_true", help="Use LoRA")
    parser.add_argument("--use_qlora", action="store_true", help="Use QLoRA (4-bit)")
    parser.add_argument("--lora_r", type=int, default=64, help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=128, help="LoRA alpha")
    parser.add_argument("--lora_dropout", type=float, default=0.05, help="LoRA dropout")
    
    # Data arguments
    parser.add_argument("--dataset_name", type=str, default="medical_qa",
                        help="Dataset name")
    parser.add_argument("--train_file", type=str, default=None,
                        help="Training data file")
    parser.add_argument("--validation_file", type=str, default=None,
                        help="Validation data file")
    parser.add_argument("--max_seq_length", type=int, default=2048,
                        help="Maximum sequence length")
    
    # Training arguments
    parser.add_argument("--output_dir", type=str, default="./output",
                        help="Output directory")
    parser.add_argument("--num_train_epochs", type=int, default=3,
                        help="Number of training epochs")
    parser.add_argument("--per_device_train_batch_size", type=int, default=4,
                        help="Training batch size per device")
    parser.add_argument("--per_device_eval_batch_size", type=int, default=4,
                        help="Eval batch size per device")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4,
                        help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=2e-4,
                        help="Learning rate")
    parser.add_argument("--warmup_ratio", type=float, default=0.03,
                        help="Warmup ratio")
    parser.add_argument("--weight_decay", type=float, default=0.001,
                        help="Weight decay")
    
    # Other
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--bf16", action="store_true", help="Use bfloat16")
    parser.add_argument("--fp16", action="store_true", help="Use float16")
    parser.add_argument("--gradient_checkpointing", action="store_true",
                        help="Enable gradient checkpointing")
    parser.add_argument("--trust_remote_code", action="store_true",
                        help="Trust remote code")
    parser.add_argument("--resume_from_checkpoint", type=str, default=None,
                        help="Resume from checkpoint")
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # Create config from args
    config = MedicalTrainingConfig()
    for key, value in vars(args).items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    # Initialize trainer
    trainer = MedicalPEFTTrainer(config=config)
    
    # Train
    trainer.train()


if __name__ == "__main__":
    main()
