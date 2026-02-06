#!/usr/bin/env python3
"""
Voice-to-Protocol Transcriber

在做实验时通过语音指令记录操作步骤和观察结果。
"""

import os
import sys
import json
import time
import wave
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum


class EntryType(Enum):
    """条目类型"""
    STEP = "步骤"
    OBSERVATION = "观察"
    NOTE = "备注"
    START = "开始"
    END = "结束"


@dataclass
class ProtocolEntry:
    """实验记录条目"""
    entry_type: EntryType
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"""### {self.entry_type.value}
**时间**: {time_str}
**内容**: {self.content}

"""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "type": self.entry_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class ProtocolTranscriber:
    """语音转录实验协议记录器"""
    
    def __init__(
        self,
        experiment_name: str = "未命名实验",
        language: str = "zh-CN",
        output_format: str = "markdown",
        save_directory: Optional[str] = None,
        auto_save_interval: int = 60,
        config: Optional[Dict] = None
    ):
        self.experiment_name = experiment_name
        self.language = language
        self.output_format = output_format
        self.auto_save_interval = auto_save_interval
        self.entries: List[ProtocolEntry] = []
        self.is_recording = False
        self.start_time: Optional[datetime] = None
        
        # 设置保存目录
        if save_directory:
            self.save_directory = Path(save_directory).expanduser()
        else:
            self.save_directory = Path.home() / "Documents" / "Experiment-Protocols"
        
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # 配置
        self.config = config or self._load_default_config()
        
        # 语音命令
        self.voice_commands = self.config.get("voice_commands", {
            "start_recording": "开始记录",
            "stop_recording": "停止记录",
            "add_observation": "观察到",
            "add_step": "步骤",
            "save_protocol": "保存记录",
            "add_note": "备注"
        })
    
    def _load_default_config(self) -> Dict:
        """加载默认配置"""
        return {
            "language": self.language,
            "output_format": self.output_format,
            "auto_save_interval": self.auto_save_interval,
            "voice_commands": {
                "start_recording": "开始记录",
                "stop_recording": "停止记录",
                "add_observation": "观察到",
                "add_step": "步骤",
                "save_protocol": "保存记录",
                "add_note": "备注"
            }
        }
    
    def add_step(self, content: str) -> None:
        """添加实验步骤"""
        entry = ProtocolEntry(EntryType.STEP, content)
        self.entries.append(entry)
        print(f"✓ [{entry.timestamp.strftime('%H:%M:%S')}] 步骤: {content}")
    
    def add_observation(self, content: str) -> None:
        """添加观察结果"""
        entry = ProtocolEntry(EntryType.OBSERVATION, content)
        self.entries.append(entry)
        print(f"✓ [{entry.timestamp.strftime('%H:%M:%S')}] 观察: {content}")
    
    def add_note(self, content: str) -> None:
        """添加备注"""
        entry = ProtocolEntry(EntryType.NOTE, content)
        self.entries.append(entry)
        print(f"✓ [{entry.timestamp.strftime('%H:%M:%S')}] 备注: {content}")
    
    def start_recording(self) -> None:
        """开始记录"""
        self.is_recording = True
        self.start_time = datetime.now()
        entry = ProtocolEntry(EntryType.START, "实验开始")
        self.entries.append(entry)
        print(f"\n🎙️ 开始记录: {self.experiment_name}")
        print(f"   时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("   可用命令: 步骤 [内容] | 观察到 [内容] | 备注 [内容] | 保存记录 | 停止记录\n")
    
    def stop_recording(self) -> str:
        """停止记录并返回保存的文件路径"""
        self.is_recording = False
        end_time = datetime.now()
        entry = ProtocolEntry(EntryType.END, f"实验结束，总时长: {self._format_duration(self.start_time, end_time)}")
        self.entries.append(entry)
        
        file_path = self.save()
        print(f"\n🛑 记录结束")
        print(f"   总条目数: {len(self.entries)}")
        print(f"   保存路径: {file_path}")
        
        return file_path
    
    def _format_duration(self, start: Optional[datetime], end: datetime) -> str:
        """格式化时长"""
        if not start:
            return "未知"
        duration = end - start
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def save(self) -> str:
        """保存实验记录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{self.experiment_name.replace(' ', '_')}_{timestamp}"
        
        if self.output_format == "markdown":
            file_path = self.save_directory / f"{filename_base}.md"
            self._save_markdown(file_path)
        elif self.output_format == "json":
            file_path = self.save_directory / f"{filename_base}.json"
            self._save_json(file_path)
        elif self.output_format == "txt":
            file_path = self.save_directory / f"{filename_base}.txt"
            self._save_text(file_path)
        else:
            # 默认 Markdown
            file_path = self.save_directory / f"{filename_base}.md"
            self._save_markdown(file_path)
        
        return str(file_path)
    
    def _save_markdown(self, file_path: Path) -> None:
        """保存为 Markdown 格式"""
        with open(file_path, 'w', encoding='utf-8') as f:
            # 标题
            f.write(f"# 实验记录: {self.experiment_name}\n\n")
            
            # 元信息
            if self.start_time:
                f.write(f"**日期**: {self.start_time.strftime('%Y-%m-%d')}\n")
                f.write(f"**开始时间**: {self.start_time.strftime('%H:%M:%S')}\n")
            f.write(f"**保存时间**: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"**条目数**: {len(self.entries)}\n\n")
            f.write("---\n\n")
            
            # 条目
            for entry in self.entries:
                f.write(entry.to_markdown())
            
            f.write("---\n\n")
            f.write(f"*由 Voice-to-Protocol Transcriber 生成*\n")
    
    def _save_json(self, file_path: Path) -> None:
        """保存为 JSON 格式"""
        data = {
            "experiment_name": self.experiment_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": datetime.now().isoformat(),
            "entries": [entry.to_dict() for entry in self.entries]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_text(self, file_path: Path) -> None:
        """保存为纯文本格式"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"实验记录: {self.experiment_name}\n")
            f.write("=" * 50 + "\n\n")
            
            if self.start_time:
                f.write(f"日期: {self.start_time.strftime('%Y-%m-%d')}\n")
                f.write(f"开始时间: {self.start_time.strftime('%H:%M:%S')}\n")
            f.write(f"保存时间: {datetime.now().strftime('%H:%M:%S')}\n\n")
            
            for entry in self.entries:
                time_str = entry.timestamp.strftime("%H:%M:%S")
                f.write(f"[{time_str}] [{entry.entry_type.value}] {entry.content}\n")
    
    def process_text_input(self, text: str) -> bool:
        """处理文本输入，返回是否继续"""
        text = text.strip()
        
        if not text:
            return True
        
        # 检查命令
        cmds = self.voice_commands
        
        if text == cmds["stop_recording"]:
            self.stop_recording()
            return False
        
        if text == cmds["save_protocol"]:
            file_path = self.save()
            print(f"💾 已保存: {file_path}")
            return True
        
        # 解析指令
        if text.startswith(cmds["add_step"]):
            content = text[len(cmds["add_step"]):].strip()
            if content:
                self.add_step(content)
            else:
                print("⚠️ 请提供步骤内容")
            return True
        
        if text.startswith(cmds["add_observation"]):
            content = text[len(cmds["add_observation"]):].strip()
            if content:
                self.add_observation(content)
            else:
                print("⚠️ 请提供观察内容")
            return True
        
        if text.startswith(cmds["add_note"]):
            content = text[len(cmds["add_note"]):].strip()
            if content:
                self.add_note(content)
            else:
                print("⚠️ 请提供备注内容")
            return True
        
        # 默认作为步骤处理
        self.add_step(text)
        return True
    
    def start_listening_text(self) -> None:
        """启动文本交互模式"""
        self.start_recording()
        
        try:
            while True:
                try:
                    text = input("> ")
                    if not self.process_text_input(text):
                        break
                except KeyboardInterrupt:
                    print("\n")
                    self.stop_recording()
                    break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            self.stop_recording()


def load_config(config_path: Optional[str] = None) -> Dict:
    """加载配置文件"""
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = Path.home() / ".openclaw" / "config" / "voice-to-protocol-transcriber.json"
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Voice-to-Protocol Transcriber - 语音记录实验协议",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --experiment "细胞培养实验"
  python main.py --config myconfig.json --lang en-US
  python main.py --output json --save-dir ~/MyExperiments
        """
    )
    
    parser.add_argument(
        "--experiment", "-e",
        default="未命名实验",
        help="实验名称 (默认: 未命名实验)"
    )
    
    parser.add_argument(
        "--lang", "-l",
        default="zh-CN",
        help="识别语言 (默认: zh-CN)"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="markdown",
        choices=["markdown", "json", "txt"],
        help="输出格式 (默认: markdown)"
    )
    
    parser.add_argument(
        "--save-dir", "-s",
        help="保存目录 (默认: ~/Documents/Experiment-Protocols)"
    )
    
    parser.add_argument(
        "--text-mode", "-t",
        action="store_true",
        help="文本交互模式 (无需语音输入)"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 命令行参数覆盖配置
    if args.lang:
        config["language"] = args.lang
    if args.output:
        config["output_format"] = args.output
    if args.save_dir:
        config["save_directory"] = args.save_dir
    
    # 创建转录器
    transcriber = ProtocolTranscriber(
        experiment_name=args.experiment,
        language=config.get("language", "zh-CN"),
        output_format=config.get("output_format", "markdown"),
        save_directory=config.get("save_directory"),
        config=config
    )
    
    # 启动
    print("=" * 50)
    print("🧪 Voice-to-Protocol Transcriber")
    print("   实验语音记录助手 v1.0.0")
    print("=" * 50)
    
    # 文本模式（简化版，无需语音依赖）
    transcriber.start_listening_text()


if __name__ == "__main__":
    main()
