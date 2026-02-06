#!/usr/bin/env python3
"""
SMILES De-salter
批量处理化学结构字符串，去除盐离子部分，仅保留活性母核。

Author: OpenClaw Skill Hub
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
except ImportError:
    print("Error: RDKit is required. Install with: pip install rdkit", file=sys.stderr)
    sys.exit(1)


def get_molecule_size(mol: Chem.Mol) -> int:
    """
    获取分子大小（以重原子数计）
    
    Args:
        mol: RDKit Mol 对象
    
    Returns:
        重原子数量
    """
    return mol.GetNumHeavyAtoms()


def is_likely_salt(mol: Chem.Mol) -> bool:
    """
    判断分子是否可能是盐离子
    
    基于启发式规则：
    - 小分子（<= 3 个重原子）
    - 常见的无机离子
    
    Args:
        mol: RDKit Mol 对象
    
    Returns:
        是否可能是盐
    """
    heavy_atoms = mol.GetNumHeavyAtoms()
    
    # 极小的分子很可能是盐
    if heavy_atoms <= 2:
        return True
    
    # 获取分子式
    formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
    
    # 常见盐离子的简单模式
    common_salts = ['Cl', 'Br', 'F', 'I', 'Na', 'K', 'Ca', 'Mg', 'Zn', 'Fe']
    # 如果只包含常见盐和少量原子
    if heavy_atoms <= 3:
        for salt in common_salts:
            if salt in formula:
                return True
    
    return False


def desalt_smiles(smiles: str, keep_largest: bool = True) -> Tuple[str, str]:
    """
    去除 SMILES 字符串中的盐离子
    
    Args:
        smiles: 输入的 SMILES 字符串
        keep_largest: 是否保留最大的组分（按重原子数）
    
    Returns:
        (处理后的 SMILES, 状态信息)
    """
    if not smiles or not smiles.strip():
        return "", "empty_input"
    
    smiles = smiles.strip()
    
    # 解析 SMILES
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return smiles, "invalid_smiles"
    
    # 按 '.' 拆分组分
    # 注意：使用 RDKit 的 SaltStripper 或手动拆分
    frags = smiles.split('.')
    
    if len(frags) <= 1:
        # 没有盐结构
        return smiles, "no_salt"
    
    # 解析每个组分
    valid_frags = []
    for frag in frags:
        frag = frag.strip()
        if not frag:
            continue
        frag_mol = Chem.MolFromSmiles(frag)
        if frag_mol is not None:
            valid_frags.append((frag, frag_mol))
    
    if not valid_frags:
        return smiles, "invalid_smiles"
    
    if len(valid_frags) == 1:
        return valid_frags[0][0], "no_salt"
    
    if keep_largest:
        # 按分子大小排序，保留最大的
        valid_frags.sort(key=lambda x: get_molecule_size(x[1]), reverse=True)
        
        # 返回最大的组分
        largest_frag, largest_mol = valid_frags[0]
        
        # 检查是否最大组分也被认为是盐（异常情况）
        if is_likely_salt(largest_mol) and len(valid_frags) > 1:
            # 找第一个非盐的大分子
            for frag, frag_mol in valid_frags:
                if not is_likely_salt(frag_mol):
                    return frag, "success"
        
        return largest_frag, "success"
    else:
        # 返回所有非盐组分（用 . 连接）
        non_salt_frags = []
        for frag, frag_mol in valid_frags:
            if not is_likely_salt(frag_mol):
                non_salt_frags.append(frag)
        
        if not non_salt_frags:
            # 所有都是盐，返回最大的那个
            valid_frags.sort(key=lambda x: get_molecule_size(x[1]), reverse=True)
            return valid_frags[0][0], "all_salts"
        
        return '.'.join(non_salt_frags), "success"


def process_file(input_path: str, output_path: str, column: str = "smiles", 
                 keep_largest: bool = True) -> None:
    """
    处理文件中的 SMILES
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        column: SMILES 列名
        keep_largest: 是否保留最大组分
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # 检测文件类型并读取
    suffix = input_file.suffix.lower()
    
    try:
        if suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(input_path)
        elif suffix in ['.tsv', '.txt']:
            import pandas as pd
            if suffix == '.tsv':
                df = pd.read_csv(input_path, sep='\t')
            else:
                # 尝试检测分隔符
                df = pd.read_csv(input_path, sep=None, engine='python')
        elif suffix == '.smi' or suffix == '.smiles':
            # 纯 SMILES 文件
            import pandas as pd
            with open(input_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            df = pd.DataFrame({column: lines})
        else:
            # 默认尝试 CSV
            import pandas as pd
            df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 检查列是否存在
    if column not in df.columns:
        print(f"Error: Column '{column}' not found in input file.", file=sys.stderr)
        print(f"Available columns: {', '.join(df.columns)}", file=sys.stderr)
        sys.exit(1)
    
    # 处理每一行
    results = []
    statuses = []
    
    for smiles in df[column]:
        if pd.isna(smiles):
            results.append("")
            statuses.append("empty_input")
        else:
            desalted, status = desalt_smiles(str(smiles), keep_largest)
            results.append(desalted)
            statuses.append(status)
    
    # 添加结果列
    df['desalted_smiles'] = results
    df['status'] = statuses
    
    # 保存结果
    try:
        output_suffix = Path(output_path).suffix.lower()
        if output_suffix == '.csv':
            df.to_csv(output_path, index=False)
        elif output_suffix in ['.tsv', '.txt']:
            df.to_csv(output_path, sep='\t', index=False)
        else:
            df.to_csv(output_path, index=False)
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 统计信息
    total = len(df)
    success = statuses.count('success')
    no_salt = statuses.count('no_salt')
    invalid = statuses.count('invalid_smiles')
    empty = statuses.count('empty_input')
    
    print(f"\nProcessing complete!")
    print(f"Total records: {total}")
    print(f"  - Successfully desalted: {success}")
    print(f"  - No salt found: {no_salt}")
    print(f"  - Invalid SMILES: {invalid}")
    print(f"  - Empty input: {empty}")


def main():
    parser = argparse.ArgumentParser(
        description='SMILES De-salter - Remove salt ions from chemical structures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 处理 CSV 文件
  python main.py -i input.csv -o output.csv -c smiles
  
  # 处理纯 SMILES 文件
  python main.py -i compounds.smi -o result.csv
  
  # 单条处理
  python main.py -s "CCO.[Na+]"
  
  # 保留所有非盐组分（不只保留最大的）
  python main.py -i input.csv --keep-largest false
        """
    )
    
    parser.add_argument('-i', '--input', type=str, help='Input file path (CSV/TSV/SMI)')
    parser.add_argument('-o', '--output', type=str, default='desalted_output.csv',
                        help='Output file path (default: desalted_output.csv)')
    parser.add_argument('-c', '--column', type=str, default='smiles',
                        help='Column name containing SMILES (default: smiles)')
    parser.add_argument('-s', '--smiles', type=str, help='Single SMILES string to process')
    parser.add_argument('-k', '--keep-largest', type=bool, default=True,
                        help='Keep the largest fragment (default: True)')
    
    args = parser.parse_args()
    
    # 单条处理模式
    if args.smiles:
        result, status = desalt_smiles(args.smiles, args.keep_largest)
        print(f"Input:    {args.smiles}")
        print(f"Output:   {result}")
        print(f"Status:   {status}")
        return
    
    # 文件处理模式
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    process_file(args.input, args.output, args.column, args.keep_largest)


if __name__ == '__main__':
    main()
