#!/usr/bin/env python3
"""
Protein Docking Configurator
为分子对接软件准备输入文件，自动确定Grid Box的中心和大小
支持AutoDock Vina、AutoDock4等主流对接软件
"""

import argparse
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union


class PDBParser:
    """解析PDB文件，提取原子坐标信息"""
    
    ATOM_RECORD_TYPES = ('ATOM', 'HETATM')
    
    @staticmethod
    def parse(pdb_file: str) -> List[Dict]:
        """
        解析PDB文件，返回原子列表
        
        Returns:
            List[Dict]: 原子信息字典列表，包含:
                - atom_id: 原子序号
                - atom_name: 原子名称
                - res_name: 残基名称
                - chain_id: 链ID
                - res_seq: 残基序号
                - x, y, z: 坐标
                - element: 元素符号
        """
        atoms = []
        
        with open(pdb_file, 'r') as f:
            for line in f:
                record_type = line[:6].strip()
                
                if record_type not in PDBParser.ATOM_RECORD_TYPES:
                    continue
                
                try:
                    atom = {
                        'atom_id': int(line[6:11].strip()),
                        'atom_name': line[12:16].strip(),
                        'alt_loc': line[16].strip(),
                        'res_name': line[17:20].strip(),
                        'chain_id': line[21].strip() or 'A',
                        'res_seq': int(line[22:26].strip()),
                        'x': float(line[30:38].strip()),
                        'y': float(line[38:46].strip()),
                        'z': float(line[46:54].strip()),
                        'element': line[76:78].strip() if len(line) > 76 else ''
                    }
                    atoms.append(atom)
                except (ValueError, IndexError):
                    continue
        
        return atoms
    
    @staticmethod
    def get_residue_atoms(atoms: List[Dict], chain_id: str, res_seq: int) -> List[Dict]:
        """获取指定残基的所有原子"""
        return [a for a in atoms if a['chain_id'] == chain_id and a['res_seq'] == res_seq]
    
    @staticmethod
    def calculate_center(atoms: List[Dict]) -> Tuple[float, float, float]:
        """计算原子集合的几何中心"""
        if not atoms:
            raise ValueError("No atoms provided for center calculation")
        
        n = len(atoms)
        cx = sum(a['x'] for a in atoms) / n
        cy = sum(a['y'] for a in atoms) / n
        cz = sum(a['z'] for a in atoms) / n
        
        return (cx, cy, cz)
    
    @staticmethod
    def calculate_bounding_box(atoms: List[Dict], padding: float = 0.0) -> Tuple[float, float, float]:
        """计算包围盒尺寸"""
        if not atoms:
            raise ValueError("No atoms provided for bounding box calculation")
        
        xs = [a['x'] for a in atoms]
        ys = [a['y'] for a in atoms]
        zs = [a['z'] for a in atoms]
        
        size_x = max(xs) - min(xs) + 2 * padding
        size_y = max(ys) - min(ys) + 2 * padding
        size_z = max(zs) - min(zs) + 2 * padding
        
        return (size_x, size_y, size_z)


class GridBoxCalculator:
    """计算Grid Box的中心和尺寸"""
    
    DEFAULT_SIZE = 20.0  # 默认Box大小 (Å)
    DEFAULT_PADDING = 5.0  # 默认padding (Å)
    
    def __init__(self):
        self.center_x = 0.0
        self.center_y = 0.0
        self.center_z = 0.0
        self.size_x = self.DEFAULT_SIZE
        self.size_y = self.DEFAULT_SIZE
        self.size_z = self.DEFAULT_SIZE
    
    def from_residues(self, receptor_file: str, residue_specs: List[str]) -> 'GridBoxCalculator':
        """
        基于活性位点残基计算Grid Box
        
        Args:
            receptor_file: 受体PDB文件路径
            residue_specs: 残基规格列表，格式: ["A:120", "A:145", ...]
        """
        atoms = PDBParser.parse(receptor_file)
        
        selected_atoms = []
        for spec in residue_specs:
            chain_id, res_seq = self._parse_residue_spec(spec)
            residue_atoms = PDBParser.get_residue_atoms(atoms, chain_id, res_seq)
            selected_atoms.extend(residue_atoms)
        
        if not selected_atoms:
            raise ValueError(f"No atoms found for residues: {residue_specs}")
        
        self.center_x, self.center_y, self.center_z = PDBParser.calculate_center(selected_atoms)
        
        # 根据残基范围自动调整Box大小
        self.size_x, self.size_y, self.size_z = PDBParser.calculate_bounding_box(
            selected_atoms, padding=self.DEFAULT_PADDING
        )
        
        # 确保最小尺寸
        self.size_x = max(self.size_x, self.DEFAULT_SIZE)
        self.size_y = max(self.size_y, self.DEFAULT_SIZE)
        self.size_z = max(self.size_z, self.DEFAULT_SIZE)
        
        return self
    
    def from_ligand(self, ligand_file: str, padding: float = 5.0) -> 'GridBoxCalculator':
        """
        基于参考配体计算Grid Box
        
        Args:
            ligand_file: 配体PDB/MOL文件路径
            padding: 配体周围的padding大小 (Å)
        """
        atoms = PDBParser.parse(ligand_file)
        
        if not atoms:
            raise ValueError(f"No atoms found in ligand file: {ligand_file}")
        
        self.center_x, self.center_y, self.center_z = PDBParser.calculate_center(atoms)
        self.size_x, self.size_y, self.size_z = PDBParser.calculate_bounding_box(atoms, padding=padding)
        
        return self
    
    def set_manual(self, center_x: float, center_y: float, center_z: float,
                   size_x: float, size_y: float, size_z: float) -> 'GridBoxCalculator':
        """手动设置Grid Box参数"""
        self.center_x = center_x
        self.center_y = center_y
        self.center_z = center_z
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        return self
    
    def _parse_residue_spec(self, spec: str) -> Tuple[str, int]:
        """解析残基规格，如 'A:120' -> ('A', 120)"""
        match = re.match(r'^([A-Za-z]?):?(\d+)$', spec.strip())
        if match:
            chain = match.group(1) or 'A'
            res_seq = int(match.group(2))
            return (chain, res_seq)
        raise ValueError(f"Invalid residue specification: {spec}. Expected format: 'A:120' or '120'")
    
    def get_params(self) -> Dict[str, float]:
        """获取Grid Box参数字典"""
        return {
            'center_x': self.center_x,
            'center_y': self.center_y,
            'center_z': self.center_z,
            'size_x': self.size_x,
            'size_y': self.size_y,
            'size_z': self.size_z
        }


class DockingConfigurator:
    """分子对接配置生成器"""
    
    def __init__(self):
        self.grid_calculator = GridBoxCalculator()
        self.receptor_file = None
    
    def from_active_site(self, receptor_file: str, residue_specs: List[str]) -> 'DockingConfigurator':
        """
        基于活性位点残基初始化
        
        Args:
            receptor_file: 受体PDB文件路径
            residue_specs: 残基规格列表，如 ["A:120", "A:145"]
        """
        self.receptor_file = receptor_file
        self.grid_calculator.from_residues(receptor_file, residue_specs)
        return self
    
    def from_reference_ligand(self, receptor_file: str, ligand_file: str, 
                               padding: float = 5.0) -> 'DockingConfigurator':
        """
        基于参考配体初始化
        
        Args:
            receptor_file: 受体PDB文件路径
            ligand_file: 参考配体文件路径
            padding: 配体周围的padding大小
        """
        self.receptor_file = receptor_file
        self.grid_calculator.from_ligand(ligand_file, padding=padding)
        return self
    
    def set_grid_params(self, center_x: float, center_y: float, center_z: float,
                        size_x: float, size_y: float, size_z: float) -> 'DockingConfigurator':
        """手动设置Grid Box参数"""
        self.grid_calculator.set_manual(center_x, center_y, center_z, size_x, size_y, size_z)
        return self
    
    def write_vina_config(self, output_file: str, ligand_file: str = 'ligand.pdbqt',
                         out_file: str = 'out.pdbqt', exhaustiveness: int = 32,
                         num_modes: int = 9, energy_range: int = 4,
                         cpu: int = 1, seed: Optional[int] = None) -> str:
        """
        生成AutoDock Vina配置文件
        
        Args:
            output_file: 输出配置文件路径
            ligand_file: 配体文件路径
            out_file: 输出对接构象文件路径
            exhaustiveness: 搜索详尽度
            num_modes: 输出构象数量
            energy_range: 能量范围 (kcal/mol)
            cpu: 使用的CPU核心数
            seed: 随机种子
        
        Returns:
            str: 生成的配置文件内容
        """
        params = self.grid_calculator.get_params()
        
        lines = [
            "# AutoDock Vina Configuration File",
            f"# Generated by Protein Docking Configurator",
            "",
            f"receptor = {self.receptor_file or 'receptor.pdbqt'}",
            f"ligand = {ligand_file}",
            "",
            f"out = {out_file}",
            "",
            f"center_x = {params['center_x']:.3f}",
            f"center_y = {params['center_y']:.3f}",
            f"center_z = {params['center_z']:.3f}",
            "",
            f"size_x = {params['size_x']:.3f}",
            f"size_y = {params['size_y']:.3f}",
            f"size_z = {params['size_z']:.3f}",
            "",
            f"exhaustiveness = {exhaustiveness}",
            f"num_modes = {num_modes}",
            f"energy_range = {energy_range}",
            f"cpu = {cpu}",
        ]
        
        if seed is not None:
            lines.append(f"seed = {seed}")
        
        content = "\n".join(lines)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        return content
    
    def write_autodock4_gpf(self, output_file: str, receptor_name: Optional[str] = None,
                            spacing: float = 0.375, npts: Optional[Tuple[int, int, int]] = None) -> str:
        """
        生成AutoDock4 Grid Parameter File (GPF)
        
        Args:
            output_file: 输出GPF文件路径
            receptor_name: 受体名称（默认为文件名）
            spacing: 网格间距 (Å)
            npts: 网格点数 (x, y, z)，自动计算如果为None
        
        Returns:
            str: 生成的GPF内容
        """
        params = self.grid_calculator.get_params()
        
        if receptor_name is None and self.receptor_file:
            receptor_name = Path(self.receptor_file).stem
        elif receptor_name is None:
            receptor_name = "receptor"
        
        # 计算网格点数 (必须是偶数，且size = npts * spacing)
        if npts is None:
            npts_x = int(params['size_x'] / spacing) // 2 * 2  # 确保为偶数
            npts_y = int(params['size_y'] / spacing) // 2 * 2
            npts_z = int(params['size_z'] / spacing) // 2 * 2
            # 最小点数
            npts_x = max(npts_x, 60)
            npts_y = max(npts_y, 60)
            npts_z = max(npts_z, 60)
        else:
            npts_x, npts_y, npts_z = npts
        
        lines = [
            "# AutoDock4 Grid Parameter File",
            f"# Generated by Protein Docking Configurator",
            "",
            f"npts {npts_x} {npts_y} {npts_z}   # num.grid points in xyz",
            f"gridfld {receptor_name}.maps.fld   # grid_data_file",
            f"spacing {spacing}                  # spacing (A)",
            "",
            f"receptor_types A C HD N NA OA SA S   # receptor atom types",
            f"ligand_types A C HD N NA OA SA S Cl   # ligand atom types",
            "",
            f"receptor {receptor_name}.pdbqt   # macromolecule",
            f"gridcenter {params['center_x']:.3f} {params['center_y']:.3f} {params['center_z']:.3f}",
            f"smooth 0.5                        # store minimum energy w/in rad(A)",
            "",
            f"map {receptor_name}.A.map         # atom-specific affinity map",
            f"map {receptor_name}.C.map",
            f"map {receptor_name}.HD.map",
            f"map {receptor_name}.N.map",
            f"map {receptor_name}.NA.map",
            f"map {receptor_name}.OA.map",
            f"map {receptor_name}.SA.map",
            f"map {receptor_name}.S.map",
            f"map {receptor_name}.Cl.map",
            "",
            f"elecmap {receptor_name}.e.map     # electrostatic potential map",
            f"dsolvmap {receptor_name}.d.map    # desolvation potential map",
            "",
            "dielectric -0.1465                # <0, AD4 distance-dep.diel;>0, constant",
        ]
        
        content = "\n".join(lines)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        return content
    
    def print_summary(self):
        """打印Grid Box参数摘要"""
        params = self.grid_calculator.get_params()
        print("\n" + "="*50)
        print("Grid Box Configuration Summary")
        print("="*50)
        print(f"Center: ({params['center_x']:.3f}, {params['center_y']:.3f}, {params['center_z']:.3f})")
        print(f"Size:   ({params['size_x']:.3f}, {params['size_y']:.3f}, {params['size_z']:.3f})")
        print(f"Volume: {params['size_x'] * params['size_y'] * params['size_z']:.1f} Å³")
        print("="*50)


def parse_residue_list(residue_str: str) -> List[str]:
    """解析残基列表字符串，如 'A:120,A:145,A:189' -> ['A:120', 'A:145', 'A:189']"""
    return [r.strip() for r in residue_str.split(',')]


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='Protein Docking Configurator - 为分子对接准备输入文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基于活性位点残基
  python main.py --receptor protein.pdb --active-site-residues "A:120,A:145" --software vina
  
  # 基于参考配体
  python main.py --receptor protein.pdb --reference-ligand ligand.pdb --software vina
  
  # 手动指定参数
  python main.py --receptor protein.pdb --center-x 10.5 --center-y -5.2 --center-z 20.1 \\
                 --size-x 20 --size-y 20 --size-z 20 --software vina
        """
    )
    
    # 必需参数
    parser.add_argument('--receptor', required=True, help='受体蛋白PDB文件路径')
    parser.add_argument('--software', required=True, choices=['vina', 'autodock4'],
                       help='对接软件类型')
    
    # Grid Box定义方式（三选一）
    box_group = parser.add_mutually_exclusive_group()
    box_group.add_argument('--active-site-residues', type=str,
                          help='活性位点残基列表，格式: "A:120,A:145,A:189"')
    box_group.add_argument('--reference-ligand', type=str,
                          help='参考配体PDB/MOL文件路径')
    
    # 手动Box参数
    parser.add_argument('--center-x', type=float, help='Grid Box中心X坐标')
    parser.add_argument('--center-y', type=float, help='Grid Box中心Y坐标')
    parser.add_argument('--center-z', type=float, help='Grid Box中心Z坐标')
    parser.add_argument('--size-x', type=float, default=20.0, help='Grid Box X尺寸 (Å)')
    parser.add_argument('--size-y', type=float, default=20.0, help='Grid Box Y尺寸 (Å)')
    parser.add_argument('--size-z', type=float, default=20.0, help='Grid Box Z尺寸 (Å)')
    
    # AutoDock4参数
    parser.add_argument('--spacing', type=float, default=0.375,
                       help='网格间距 (仅AutoDock4，默认0.375Å)')
    
    # AutoDock Vina参数
    parser.add_argument('--exhaustiveness', type=int, default=32,
                       help='搜索详尽度 (仅Vina，默认32)')
    parser.add_argument('--num-modes', type=int, default=9,
                       help='输出构象数量 (仅Vina，默认9)')
    
    # 输出参数
    parser.add_argument('--output', '-o', type=str, help='输出文件路径')
    parser.add_argument('--padding', type=float, default=5.0,
                       help='配体周围padding大小 (Å)')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    # 创建配置器
    config = DockingConfigurator()
    
    try:
        # 确定Grid Box参数
        if args.active_site_residues:
            residues = parse_residue_list(args.active_site_residues)
            config.from_active_site(args.receptor, residues)
            if not args.quiet:
                print(f"Calculated grid box from {len(residues)} active site residue(s)")
        
        elif args.reference_ligand:
            config.from_reference_ligand(args.receptor, args.reference_ligand, padding=args.padding)
            if not args.quiet:
                print(f"Calculated grid box from reference ligand with {args.padding}Å padding")
        
        elif args.center_x is not None and args.center_y is not None and args.center_z is not None:
            config.set_grid_params(args.center_x, args.center_y, args.center_z,
                                  args.size_x, args.size_y, args.size_z)
            if not args.quiet:
                print("Using manually specified grid box parameters")
        
        else:
            parser.error("必须指定一种Grid Box定义方式: --active-site-residues, --reference-ligand, 或 --center-x/y/z")
        
        # 打印摘要
        if not args.quiet:
            config.print_summary()
        
        # 生成配置文件
        if args.software == 'vina':
            default_output = 'vina_config.txt'
            output_file = args.output or default_output
            config.write_vina_config(output_file, exhaustiveness=args.exhaustiveness, num_modes=args.num_modes)
            if not args.quiet:
                print(f"\nAutoDock Vina config written to: {output_file}")
        
        elif args.software == 'autodock4':
            default_output = Path(args.receptor).stem + '.gpf'
            output_file = args.output or default_output
            config.write_autodock4_gpf(output_file, spacing=args.spacing)
            if not args.quiet:
                print(f"\nAutoDock4 GPF written to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
