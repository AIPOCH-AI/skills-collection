# Low-Resource AI Researcher

基于参数高效微调(PEFT)技术，在消费级显卡或单张A100上训练高性能医疗模型。

## 快速开始

```python
from skills.low_resource_ai_researcher.scripts.main import MedicalPEFTTrainer

# 初始化训练器
trainer = MedicalPEFTTrainer(
    model_name="meta-llama/Llama-2-7b-hf",
    task="medical_qa"
)

# 使用QLoRA训练（适合24GB显存）
trainer.train(
    output_dir="./medical_lora_model",
    num_epochs=3,
    batch_size=4,
    use_qlora=True
)
```

## 命令行使用

```bash
# QLoRA训练（消费级显卡）
python scripts/main.py \
    --model_name_or_path meta-llama/Llama-2-7b-hf \
    --dataset_name medical_qa \
    --output_dir ./output \
    --use_qlora \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --num_train_epochs 3

# LoRA训练（A100）
python scripts/main.py \
    --model_name_or_path meta-llama/Llama-2-13b-hf \
    --dataset_name medqa \
    --output_dir ./output \
    --use_lora \
    --bf16 \
    --per_device_train_batch_size 8
```

## 硬件配置建议

| 配置 | GPU | 量化 | 最大模型 | 批次大小 |
|------|-----|------|----------|----------|
| 消费级 | RTX 3090/4090 (24GB) | QLoRA 4-bit | 70B | 1-2 |
| 单卡A100 | A100 40GB/80GB | LoRA 8-bit | 70B | 4-8 |

## 文件结构

```
low-resource-ai-researcher/
├── SKILL.md           # 技能文档
├── scripts/
│   ├── __init__.py    # 包初始化
│   └── main.py        # 主训练脚本
└── examples/          # 示例配置（可选）
```
