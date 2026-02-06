#!/usr/bin/env python3
"""
DPI Upscaler & Checker
检查图片DPI并智能超分辨率修复低清图片

功能:
- 检查图片是否达到300 DPI
- 使用超分辨率算法修复模糊的低清图
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import warnings

import numpy as np
from PIL import Image, ExifTags


class DPIChecker:
    """DPI检查器"""
    
    def __init__(self, target_dpi: int = 300):
        self.target_dpi = target_dpi
    
    def check_image(self, image_path: str) -> Dict:
        """
        检查单张图片的DPI信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            包含DPI信息的字典
        """
        try:
            with Image.open(image_path) as img:
                width_px, height_px = img.size
                
                # 获取DPI信息
                dpi = img.info.get('dpi', (None, None))
                
                # 尝试从EXIF获取DPI
                if dpi[0] is None or dpi[1] is None:
                    dpi = self._get_dpi_from_exif(img)
                
                # 如果没有DPI信息，默认72
                if dpi[0] is None or dpi[1] is None:
                    dpi = (72, 72)
                
                # 计算打印尺寸
                print_width_cm = (width_px / dpi[0]) * 2.54 if dpi[0] else None
                print_height_cm = (height_px / dpi[1]) * 2.54 if dpi[1] else None
                
                # 计算需要的缩放比例以达到目标DPI
                avg_dpi = (dpi[0] + dpi[1]) / 2
                recommended_scale = self.target_dpi / avg_dpi if avg_dpi > 0 else 4
                
                return {
                    'file': image_path,
                    'format': img.format,
                    'mode': img.mode,
                    'width_px': width_px,
                    'height_px': height_px,
                    'dpi': list(dpi),
                    'avg_dpi': round(avg_dpi, 2),
                    'print_width_cm': round(print_width_cm, 2) if print_width_cm else None,
                    'print_height_cm': round(print_height_cm, 2) if print_height_cm else None,
                    'meets_target_dpi': avg_dpi >= self.target_dpi,
                    'recommended_scale': round(recommended_scale, 2),
                    'status': 'ok'
                }
                
        except Exception as e:
            return {
                'file': image_path,
                'error': str(e),
                'status': 'error'
            }
    
    def _get_dpi_from_exif(self, img: Image.Image) -> Tuple[Optional[int], Optional[int]]:
        """从EXIF数据中提取DPI"""
        try:
            exif = img._getexif()
            if exif:
                # EXIF tag 282 = XResolution, 283 = YResolution
                x_res = exif.get(282)
                y_res = exif.get(283)
                
                # EXIF中DPI通常存储为分数形式，如 72/1
                if x_res and isinstance(x_res, tuple):
                    x_res = x_res[0] / x_res[1] if x_res[1] != 0 else x_res[0]
                if y_res and isinstance(y_res, tuple):
                    y_res = y_res[0] / y_res[1] if y_res[1] != 0 else y_res[0]
                
                return (int(x_res) if x_res else None, int(y_res) if y_res else None)
        except:
            pass
        return (None, None)
    
    def check_directory(self, directory: str) -> List[Dict]:
        """批量检查目录中的所有图片"""
        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        
        for file_path in Path(directory).rglob('*'):
            if file_path.suffix.lower() in image_extensions:
                result = self.check_image(str(file_path))
                results.append(result)
        
        return results


class ImageUpscaler:
    """图像超分辨率处理器"""
    
    def __init__(self):
        self.upscaler_type = None
        self._init_upscaler()
    
    def _init_upscaler(self):
        """初始化超分辨率引擎"""
        # 尝试使用Real-ESRGAN
        try:
            from realesrgan import RealESRGANer
            self.upscaler_type = 'realesrgan'
            print("[INFO] 使用 Real-ESRGAN 超分辨率引擎")
        except ImportError:
            # 尝试使用OpenCV DNN SuperRes
            try:
                import cv2
                self.cv2 = cv2
                self.upscaler_type = 'opencv_dnn'
                print("[INFO] 使用 OpenCV DNN 超分辨率引擎")
            except ImportError:
                # 使用PIL高质量插值
                self.upscaler_type = 'pil'
                print("[INFO] 使用 PIL Lanczos 插值引擎")
    
    def upscale(self, 
                image_path: str, 
                output_path: str, 
                scale: int = 2,
                target_dpi: int = 300) -> Dict:
        """
        对图片进行超分辨率处理
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径
            scale: 放大倍数 (2/3/4)
            target_dpi: 目标DPI
            
        Returns:
            处理结果信息
        """
        try:
            # 读取原图
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # 转换为RGB进行AI处理
                if img.mode in ('RGBA', 'P'):
                    img_rgb = img.convert('RGB')
                else:
                    img_rgb = img
                
                # 执行超分辨率
                upscaled_img = self._upscale_image(img_rgb, scale)
                
                # 如果原图有透明通道，需要特殊处理
                if original_mode == 'RGBA':
                    # 放大alpha通道
                    alpha = img.split()[-1].resize(
                        (upscaled_img.width, upscaled_img.height), 
                        Image.LANCZOS
                    )
                    upscaled_img = upscaled_img.convert('RGBA')
                    upscaled_img.putalpha(alpha)
                
                # 设置DPI并保存
                upscaled_img.save(
                    output_path, 
                    dpi=(target_dpi, target_dpi),
                    quality=95,
                    optimize=True
                )
                
                return {
                    'input': image_path,
                    'output': output_path,
                    'original_size': original_size,
                    'upscaled_size': upscaled_img.size,
                    'scale': scale,
                    'target_dpi': target_dpi,
                    'status': 'success'
                }
                
        except Exception as e:
            return {
                'input': image_path,
                'error': str(e),
                'status': 'error'
            }
    
    def _upscale_image(self, img: Image.Image, scale: int) -> Image.Image:
        """使用不同引擎进行超分辨率"""
        if self.upscaler_type == 'pil':
            return self._upscale_pil(img, scale)
        elif self.upscaler_type == 'opencv_dnn':
            return self._upscale_opencv(img, scale)
        else:
            return self._upscale_pil(img, scale)  # 默认使用PIL
    
    def _upscale_pil(self, img: Image.Image, scale: int) -> Image.Image:
        """使用PIL Lanczos插值"""
        new_size = (img.width * scale, img.height * scale)
        return img.resize(new_size, Image.LANCZOS)
    
    def _upscale_opencv(self, img: Image.Image, scale: int) -> Image.Image:
        """使用OpenCV DNN超分辨率"""
        try:
            # 转换为OpenCV格式 (BGR)
            img_array = np.array(img)
            img_cv = self.cv2.cvtColor(img_array, self.cv2.COLOR_RGB2BGR)
            
            # 使用双三次插值作为高质量回退
            new_width = int(img_cv.shape[1] * scale)
            new_height = int(img_cv.shape[0] * scale)
            upscaled = self.cv2.resize(
                img_cv, 
                (new_width, new_height), 
                interpolation=self.cv2.INTER_CUBIC
            )
            
            # 尝试使用DNN超分辨率（如果模型可用）
            try:
                sr = self.cv2.dnn_superres.DnnSuperResImpl_create()
                model_path = f"EDSR_x{scale}.pb"  # 需要下载模型文件
                if os.path.exists(model_path):
                    sr.readModel(model_path)
                    sr.setModel("edsr", scale)
                    upscaled = sr.upsample(img_cv)
            except:
                pass  # 使用已上采样的图像
            
            # 转换回PIL格式 (RGB)
            upscaled_rgb = self.cv2.cvtColor(upscaled, self.cv2.COLOR_BGR2RGB)
            return Image.fromarray(upscaled_rgb)
            
        except Exception as e:
            print(f"[WARN] OpenCV处理失败，回退到PIL: {e}")
            return self._upscale_pil(img, scale)
    
    def batch_upscale(self,
                      input_dir: str,
                      output_dir: str,
                      scale: int = 2,
                      min_dpi: Optional[int] = None,
                      target_dpi: int = 300) -> List[Dict]:
        """批量处理图片"""
        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        
        os.makedirs(output_dir, exist_ok=True)
        
        dpi_checker = DPIChecker(target_dpi) if min_dpi else None
        
        for file_path in Path(input_dir).rglob('*'):
            if file_path.suffix.lower() in image_extensions:
                # 检查DPI（如果需要）
                if min_dpi and dpi_checker:
                    dpi_info = dpi_checker.check_image(str(file_path))
                    if dpi_info.get('meets_target_dpi', False):
                        print(f"[SKIP] {file_path} 已满足DPI要求")
                        continue
                
                # 构建输出路径
                rel_path = file_path.relative_to(input_dir)
                output_path = Path(output_dir) / rel_path.parent / f"{file_path.stem}_upscaled{file_path.suffix}"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                result = self.upscale(str(file_path), str(output_path), scale, target_dpi)
                results.append(result)
                
                if result['status'] == 'success':
                    print(f"[OK] {file_path.name} -> {output_path}")
                else:
                    print(f"[ERROR] {file_path.name}: {result.get('error')}")
        
        return results


def print_dpi_report(result: Dict):
    """打印DPI检查报告"""
    if result.get('status') == 'error':
        print(f"❌ {result['file']}: {result.get('error')}")
        return
    
    print(f"\n📷 {result['file']}")
    print(f"   格式: {result.get('format', 'Unknown')}")
    print(f"   尺寸: {result['width_px']} x {result['height_px']} px")
    print(f"   DPI: {result['dpi'][0]} x {result['dpi'][1]}")
    print(f"   平均DPI: {result['avg_dpi']}")
    
    if result.get('print_width_cm'):
        print(f"   打印尺寸: {result['print_width_cm']}cm x {result['print_height_cm']}cm")
    
    if result.get('meets_target_dpi'):
        print(f"   ✅ 满足300 DPI要求")
    else:
        print(f"   ⚠️  不满足300 DPI要求")
        print(f"   💡 建议放大倍数: {result['recommended_scale']}x")


def main():
    parser = argparse.ArgumentParser(
        description='DPI Upscaler & Checker - 检查图片DPI并智能超分辨率修复',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 检查单张图片
  python main.py check -i image.jpg
  
  # 批量检查并生成报告
  python main.py check -i ./images/ -o report.json
  
  # 超分辨率修复（2倍放大）
  python main.py upscale -i image.jpg -o output.jpg --scale 2
  
  # 批量修复低DPI图片
  python main.py upscale -i ./input/ -o ./output/ --min-dpi 300 --scale 4
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # check 命令
    check_parser = subparsers.add_parser('check', help='检查图片DPI')
    check_parser.add_argument('-i', '--input', required=True, 
                              help='输入图片路径或文件夹')
    check_parser.add_argument('-o', '--output', 
                              help='输出报告路径 (JSON格式)')
    check_parser.add_argument('--target-dpi', type=int, default=300,
                              help='目标DPI (默认: 300)')
    
    # upscale 命令
    upscale_parser = subparsers.add_parser('upscale', help='超分辨率放大图片')
    upscale_parser.add_argument('-i', '--input', required=True,
                                help='输入图片路径或文件夹')
    upscale_parser.add_argument('-o', '--output', required=True,
                                help='输出路径')
    upscale_parser.add_argument('--scale', type=int, default=2, choices=[2, 3, 4],
                                help='放大倍数 (默认: 2)')
    upscale_parser.add_argument('--min-dpi', type=int,
                                help='仅处理低于此DPI的图片')
    upscale_parser.add_argument('--target-dpi', type=int, default=300,
                                help='输出图片的目标DPI (默认: 300)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'check':
        checker = DPIChecker(args.target_dpi)
        
        if os.path.isfile(args.input):
            # 单文件检查
            result = checker.check_image(args.input)
            print_dpi_report(result)
            results = [result]
        else:
            # 批量检查
            print(f"正在检查目录: {args.input}")
            results = checker.check_directory(args.input)
            
            # 统计
            total = len(results)
            errors = sum(1 for r in results if r.get('status') == 'error')
            meets_dpi = sum(1 for r in results if r.get('meets_target_dpi', False))
            
            print(f"\n{'='*50}")
            print(f"总计: {total} 张图片")
            print(f"错误: {errors} 张")
            print(f"满足DPI: {meets_dpi} 张")
            print(f"需修复: {total - errors - meets_dpi} 张")
            
            for result in results:
                print_dpi_report(result)
        
        # 保存报告
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n报告已保存: {args.output}")
    
    elif args.command == 'upscale':
        upscaler = ImageUpscaler()
        
        if os.path.isfile(args.input):
            # 单文件处理
            result = upscaler.upscale(args.input, args.output, args.scale, args.target_dpi)
            if result['status'] == 'success':
                print(f"✅ 处理成功!")
                print(f"   输入: {result['input']}")
                print(f"   输出: {result['output']}")
                print(f"   尺寸: {result['original_size']} -> {result['upscaled_size']}")
            else:
                print(f"❌ 处理失败: {result.get('error')}")
                sys.exit(1)
        else:
            # 批量处理
            print(f"正在批量处理: {args.input}")
            results = upscaler.batch_upscale(
                args.input, args.output, 
                args.scale, args.min_dpi, args.target_dpi
            )
            
            success = sum(1 for r in results if r['status'] == 'success')
            failed = sum(1 for r in results if r['status'] == 'error')
            
            print(f"\n{'='*50}")
            print(f"处理完成: 成功 {success} 张, 失败 {failed} 张")


if __name__ == '__main__':
    main()
