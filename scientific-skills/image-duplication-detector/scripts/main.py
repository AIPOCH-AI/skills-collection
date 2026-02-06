#!/usr/bin/env python3
"""
Image Duplication Detector
利用计算机视觉(CV)算法扫描论文手稿，检测图片重复使用或局部篡改
"""

import os
import sys
import json
import argparse
import hashlib
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import time

import numpy as np
import cv2
from PIL import Image, ImageStat
import imagehash


try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: pdf2image not installed. PDF support disabled.")


@dataclass
class ImageInfo:
    """图片信息数据类"""
    path: str
    page: Optional[int] = None
    index: int = 0
    width: int = 0
    height: int = 0
    phash: Optional[str] = None
    dhash: Optional[str] = None
    ahash: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class DuplicateGroup:
    """重复图片组"""
    group_id: int
    similarity: float
    images: List[Dict]
    match_type: str  # 'exact', 'similar', 'partial'
    
    def to_dict(self):
        return {
            "group_id": self.group_id,
            "similarity": self.similarity,
            "match_type": self.match_type,
            "images": self.images
        }


@dataclass
class TamperingRegion:
    """篡改检测区域"""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    type: str  # 'ela', 'copy-move', 'noise'
    
    def to_dict(self):
        return asdict(self)


@dataclass
class TamperingResult:
    """篡改检测结果"""
    image: str
    suspicious_regions: List[TamperingRegion]
    ela_score: float
    
    def to_dict(self):
        return {
            "image": self.image,
            "ela_score": self.ela_score,
            "suspicious_regions": [r.to_dict() for r in self.suspicious_regions]
        }


class ImageDuplicationDetector:
    """图片重复与篡改检测器"""
    
    def __init__(self, threshold: float = 0.85, detect_tampering: bool = False, 
                 temp_dir: str = "./temp"):
        self.threshold = threshold
        self.detect_tampering = detect_tampering
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化ORB特征检测器
        self.orb = cv2.ORB_create(nfeatures=500)
        
        # BFMatcher用于特征匹配
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[ImageInfo]:
        """从PDF中提取图片"""
        if not PDF_SUPPORT:
            raise RuntimeError("pdf2image not installed. Cannot process PDF files.")
        
        images = []
        try:
            # 将PDF页面转换为图片
            pages = convert_from_path(pdf_path, dpi=200)
            
            for page_num, page in enumerate(pages, 1):
                # 保存页面为临时图片
                temp_path = self.temp_dir / f"page_{page_num:03d}.png"
                page.save(temp_path, "PNG")
                
                img_info = self._analyze_image(str(temp_path), page=page_num)
                images.append(img_info)
                
        except Exception as e:
            print(f"Error extracting images from PDF: {e}")
            
        return images
    
    def _analyze_image(self, image_path: str, page: Optional[int] = None) -> ImageInfo:
        """分析单张图片，提取特征"""
        pil_img = Image.open(image_path)
        width, height = pil_img.size
        
        # 计算感知哈希
        phash = str(imagehash.phash(pil_img))
        dhash = str(imagehash.dhash(pil_img))
        ahash = str(imagehash.average_hash(pil_img))
        
        return ImageInfo(
            path=image_path,
            page=page,
            width=width,
            height=height,
            phash=phash,
            dhash=dhash,
            ahash=ahash
        )
    
    def load_images_from_folder(self, folder_path: str) -> List[ImageInfo]:
        """从文件夹加载图片"""
        images = []
        folder = Path(folder_path)
        
        valid_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'}
        
        for idx, img_path in enumerate(sorted(folder.iterdir()), 1):
            if img_path.suffix.lower() in valid_extensions:
                try:
                    img_info = self._analyze_image(str(img_path), index=idx)
                    images.append(img_info)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")
        
        return images
    
    def _hash_similarity(self, hash1: str, hash2: str) -> float:
        """计算哈希相似度"""
        # 汉明距离
        distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        max_len = max(len(hash1), len(hash2))
        return 1 - (distance / max_len) if max_len > 0 else 0
    
    def _perceptual_similarity(self, img1: ImageInfo, img2: ImageInfo) -> float:
        """计算感知相似度"""
        # 组合多种哈希
        phash_sim = self._hash_similarity(img1.phash, img2.phash)
        dhash_sim = self._hash_similarity(img1.dhash, img2.dhash)
        ahash_sim = self._hash_similarity(img1.ahash, img2.ahash)
        
        # 加权平均
        return 0.5 * phash_sim + 0.3 * dhash_sim + 0.2 * ahash_sim
    
    def _orb_similarity(self, path1: str, path2: str) -> float:
        """使用ORB特征计算相似度"""
        try:
            img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # 统一尺寸
            img1 = cv2.resize(img1, (256, 256))
            img2 = cv2.resize(img2, (256, 256))
            
            kp1, des1 = self.orb.detectAndCompute(img1, None)
            kp2, des2 = self.orb.detectAndCompute(img2, None)
            
            if des1 is None or des2 is None:
                return 0.0
            
            matches = self.bf.match(des1, des2)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # 计算匹配比例
            good_matches = [m for m in matches if m.distance < 50]
            similarity = len(good_matches) / max(len(kp1), len(kp2), 1)
            
            return min(similarity, 1.0)
        except Exception as e:
            return 0.0
    
    def find_duplicates(self, images: List[ImageInfo]) -> List[DuplicateGroup]:
        """查找重复图片"""
        duplicates = []
        grouped = set()
        group_id = 0
        
        n = len(images)
        for i in range(n):
            if i in grouped:
                continue
            
            similar_images = [images[i].to_dict()]
            match_type = "exact"
            
            for j in range(i + 1, n):
                if j in grouped:
                    continue
                
                # 快速预筛选：感知哈希
                p_sim = self._perceptual_similarity(images[i], images[j])
                
                if p_sim >= self.threshold:
                    # 精确验证：ORB特征匹配
                    orb_sim = self._orb_similarity(images[i].path, images[j].path)
                    
                    combined_sim = 0.6 * p_sim + 0.4 * orb_sim
                    
                    if combined_sim >= self.threshold:
                        similar_images.append(images[j].to_dict())
                        grouped.add(j)
                        
                        if combined_sim >= 0.95:
                            match_type = "exact"
                        elif combined_sim >= 0.90:
                            match_type = "similar"
                        else:
                            match_type = "partial"
            
            if len(similar_images) > 1:
                group_id += 1
                duplicates.append(DuplicateGroup(
                    group_id=group_id,
                    similarity=p_sim,
                    images=similar_images,
                    match_type=match_type
                ))
        
        return duplicates
    
    def _ela_analysis(self, image_path: str) -> Tuple[np.ndarray, float]:
        """Error Level Analysis - 检测JPEG压缩异常"""
        try:
            # 重新压缩
            temp_buffer = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_buffer.name
            temp_buffer.close()
            
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 以固定质量重新保存
            img.save(temp_path, 'JPEG', quality=90)
            
            # 加载重新压缩的图片
            recompressed = Image.open(temp_path)
            
            # 计算差异
            original_arr = np.array(img).astype(float)
            recompressed_arr = np.array(recompressed).astype(float)
            
            # ELA = (原始 - 重压缩) * 缩放因子
            diff = np.abs(original_arr - recompressed_arr)
            ela = diff * 15  # 放大差异以便观察
            ela = np.clip(ela, 0, 255).astype(np.uint8)
            
            # 计算ELA分数（差异越大，篡改可能性越高）
            ela_score = np.mean(diff)
            
            os.unlink(temp_path)
            
            return ela, ela_score
        except Exception as e:
            return np.zeros((100, 100, 3), dtype=np.uint8), 0.0
    
    def _detect_copy_move(self, image_path: str) -> List[TamperingRegion]:
        """检测Copy-Move伪造（复制-移动）"""
        regions = []
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return regions
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 使用SIFT检测特征点
            sift = cv2.SIFT_create()
            kp, des = sift.detectAndCompute(gray, None)
            
            if des is None or len(kp) < 2:
                return regions
            
            # FLANN匹配器
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            # 寻找相似区域
            matches = flann.knnMatch(des, des, k=2)
            
            suspicious_points = []
            for i, match_pair in enumerate(matches):
                if len(match_pair) < 2:
                    continue
                m, n = match_pair
                # 低距离比表示高相似度
                if m.distance < 0.7 * n.distance and m.queryIdx != m.trainIdx:
                    pt1 = kp[m.queryIdx].pt
                    pt2 = kp[m.trainIdx].pt
                    
                    # 如果距离足够远，可能是复制-移动
                    dist = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
                    if dist > 50:  # 至少相隔50像素
                        suspicious_points.append((pt1, pt2, m.distance))
            
            # 聚类可疑点形成区域
            if len(suspicious_points) >= 3:
                # 简单聚类：找到可疑点密集的区域
                x_coords = [int(p[0][0]) for p in suspicious_points[:10]]
                y_coords = [int(p[0][1]) for p in suspicious_points[:10]]
                
                if x_coords and y_coords:
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    regions.append(TamperingRegion(
                        x=x_min - 20,
                        y=y_min - 20,
                        width=x_max - x_min + 40,
                        height=y_max - y_min + 40,
                        confidence=min(len(suspicious_points) / 20, 1.0),
                        type="copy-move"
                    ))
            
        except Exception as e:
            pass
        
        return regions
    
    def _noise_analysis(self, image_path: str) -> List[TamperingRegion]:
        """噪声分析检测"""
        regions = []
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return regions
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # 分块分析噪声
            block_size = 64
            noise_map = np.zeros((h // block_size, w // block_size))
            
            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    # 使用拉普拉斯算子估计噪声
                    laplacian = cv2.Laplacian(block, cv2.CV_64F)
                    noise_level = np.var(laplacian)
                    noise_map[i//block_size, j//block_size] = noise_level
            
            # 检测噪声异常区域
            mean_noise = np.mean(noise_map)
            std_noise = np.std(noise_map)
            
            threshold = mean_noise + 2 * std_noise
            
            for i in range(noise_map.shape[0]):
                for j in range(noise_map.shape[1]):
                    if noise_map[i, j] > threshold:
                        regions.append(TamperingRegion(
                            x=j * block_size,
                            y=i * block_size,
                            width=block_size,
                            height=block_size,
                            confidence=min((noise_map[i, j] - mean_noise) / (3 * std_noise), 1.0),
                            type="noise"
                        ))
        
        except Exception as e:
            pass
        
        return regions
    
    def detect_tampering(self, images: List[ImageInfo]) -> List[TamperingResult]:
        """检测图片篡改"""
        results = []
        
        for img_info in images:
            regions = []
            
            # ELA分析
            ela_img, ela_score = self._ela_analysis(img_info.path)
            
            if ela_score > 5:  # 阈值可调
                h, w = ela_img.shape[:2]
                # 寻找ELA高亮区域
                gray_ela = cv2.cvtColor(ela_img, cv2.COLOR_RGB2GRAY)
                _, thresh = cv2.threshold(gray_ela, 30, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    x, y, cw, ch = cv2.boundingRect(cnt)
                    if cw * ch > 100:  # 过滤小噪点
                        regions.append(TamperingRegion(
                            x=x, y=y, width=cw, height=ch,
                            confidence=min(ela_score / 20, 1.0),
                            type="ela"
                        ))
            
            # Copy-Move检测
            copy_move_regions = self._detect_copy_move(img_info.path)
            regions.extend(copy_move_regions)
            
            # 噪声分析
            noise_regions = self._noise_analysis(img_info.path)
            regions.extend(noise_regions)
            
            # 合并重叠区域
            regions = self._merge_regions(regions)
            
            if regions:
                results.append(TamperingResult(
                    image=img_info.path,
                    suspicious_regions=regions,
                    ela_score=ela_score
                ))
        
        return results
    
    def _merge_regions(self, regions: List[TamperingRegion], 
                       overlap_threshold: float = 0.3) -> List[TamperingRegion]:
        """合并重叠的检测区域"""
        if not regions:
            return []
        
        # 按置信度排序
        regions = sorted(regions, key=lambda r: r.confidence, reverse=True)
        merged = []
        
        for r in regions:
            should_merge = False
            for m in merged:
                # 计算IoU
                x1 = max(r.x, m.x)
                y1 = max(r.y, m.y)
                x2 = min(r.x + r.width, m.x + m.width)
                y2 = min(r.y + r.height, m.y + m.height)
                
                if x2 > x1 and y2 > y1:
                    intersection = (x2 - x1) * (y2 - y1)
                    union = r.width * r.height + m.width * m.height - intersection
                    iou = intersection / union if union > 0 else 0
                    
                    if iou > overlap_threshold:
                        should_merge = True
                        # 扩展合并区域
                        m.x = min(m.x, r.x)
                        m.y = min(m.y, r.y)
                        m.width = max(m.x + m.width, r.x + r.width) - m.x
                        m.height = max(m.y + m.height, r.y + r.height) - m.y
                        m.confidence = max(m.confidence, r.confidence)
                        break
            
            if not should_merge:
                merged.append(r)
        
        return merged
    
    def create_visualization(self, images: List[ImageInfo], 
                            duplicates: List[DuplicateGroup],
                            tampering: List[TamperingResult],
                            output_path: str):
        """创建可视化报告"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Rectangle
            
            fig_count = len(duplicates) + len(tampering)
            if fig_count == 0:
                return
            
            cols = min(3, fig_count)
            rows = (fig_count + cols - 1) // cols
            
            fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
            if rows == 1 and cols == 1:
                axes = np.array([axes])
            axes = axes.flatten()
            
            idx = 0
            # 绘制重复组
            for dup in duplicates:
                if idx >= len(axes):
                    break
                ax = axes[idx]
                
                # 显示第一张图
                img1 = Image.open(dup.images[0]['path'])
                ax.imshow(img1)
                ax.set_title(f"Duplicate Group {dup.group_id}\n({dup.match_type}, sim={dup.similarity:.2f})")
                ax.axis('off')
                idx += 1
            
            # 绘制篡改检测
            for tam in tampering:
                if idx >= len(axes):
                    break
                ax = axes[idx]
                
                img = Image.open(tam.image)
                ax.imshow(img)
                ax.set_title(f"Tampering: {Path(tam.image).name}\n(ELA: {tam.ela_score:.1f})")
                
                # 绘制可疑区域
                for region in tam.suspicious_regions:
                    rect = Rectangle(
                        (region.x, region.y), region.width, region.height,
                        linewidth=2, edgecolor='r', facecolor='none'
                    )
                    ax.add_patch(rect)
                    ax.text(region.x, region.y - 5, 
                           f"{region.type} ({region.confidence:.2f})",
                           color='red', fontsize=8)
                
                ax.axis('off')
                idx += 1
            
            # 隐藏未使用的子图
            for i in range(idx, len(axes)):
                axes[i].axis('off')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"Visualization saved to: {output_path}")
            
        except ImportError:
            print("matplotlib not installed. Skipping visualization.")
    
    def scan(self, input_path: str) -> Dict:
        """主扫描函数"""
        start_time = time.time()
        
        input_path = Path(input_path)
        
        # 加载图片
        if input_path.suffix.lower() == '.pdf':
            print(f"Extracting images from PDF: {input_path}")
            images = self.extract_images_from_pdf(str(input_path))
        elif input_path.is_dir():
            print(f"Loading images from folder: {input_path}")
            images = self.load_images_from_folder(str(input_path))
        else:
            # 单张图片
            images = [self._analyze_image(str(input_path))]
        
        print(f"Loaded {len(images)} images for analysis")
        
        # 检测重复
        print("Detecting duplicates...")
        duplicates = self.find_duplicates(images)
        print(f"Found {len(duplicates)} duplicate groups")
        
        # 检测篡改
        tampering = []
        if self.detect_tampering:
            print("Detecting tampering...")
            tampering = self.detect_tampering(images)
            print(f"Found {len(tampering)} suspicious images")
        
        processing_time = time.time() - start_time
        
        # 生成报告
        report = {
            "summary": {
                "total_images": len(images),
                "duplicates_found": len(duplicates),
                "tampering_detected": len(tampering),
                "processing_time": f"{processing_time:.2f}s",
                "timestamp": datetime.now().isoformat()
            },
            "duplicates": [d.to_dict() for d in duplicates],
            "tampering": [t.to_dict() for t in tampering]
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: str):
        """保存报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Image Duplication Detector - 检测论文手稿中的图片重复和篡改"
    )
    parser.add_argument("--input", "-i", required=True, 
                       help="输入PDF文件或图片文件夹路径")
    parser.add_argument("--output", "-o", default="report.json",
                       help="输出报告路径 (默认: report.json)")
    parser.add_argument("--threshold", "-t", type=float, default=0.85,
                       help="相似度阈值 (0-1), 默认0.85")
    parser.add_argument("--detect-tampering", action="store_true",
                       help="启用篡改/PS痕迹检测")
    parser.add_argument("--visualize", "-v", action="store_true",
                       help="生成可视化报告")
    parser.add_argument("--temp-dir", default="./temp",
                       help="临时文件目录")
    
    args = parser.parse_args()
    
    # 初始化检测器
    detector = ImageDuplicationDetector(
        threshold=args.threshold,
        detect_tampering=args.detect_tampering,
        temp_dir=args.temp_dir
    )
    
    # 执行扫描
    report = detector.scan(args.input)
    
    # 保存报告
    detector.save_report(report, args.output)
    
    # 生成可视化
    if args.visualize:
        viz_path = str(Path(args.output).with_suffix('.png'))
        # 重新加载图片用于可视化
        if Path(args.input).suffix.lower() == '.pdf':
            images = detector.extract_images_from_pdf(args.input)
        elif Path(args.input).is_dir():
            images = detector.load_images_from_folder(args.input)
        else:
            images = [detector._analyze_image(args.input)]
        
        duplicates = [DuplicateGroup(**d) for d in report["duplicates"]]
        tampering = []
        for t in report["tampering"]:
            regions = [TamperingRegion(**r) for r in t["suspicious_regions"]]
            tampering.append(TamperingResult(
                image=t["image"],
                suspicious_regions=regions,
                ela_score=t["ela_score"]
            ))
        
        detector.create_visualization(images, duplicates, tampering, viz_path)
    
    # 打印摘要
    summary = report["summary"]
    print("\n" + "="*50)
    print("SCAN SUMMARY")
    print("="*50)
    print(f"Total images: {summary['total_images']}")
    print(f"Duplicates found: {summary['duplicates_found']}")
    print(f"Tampering detected: {summary['tampering_detected']}")
    print(f"Processing time: {summary['processing_time']}")
    print("="*50)


if __name__ == "__main__":
    main()
