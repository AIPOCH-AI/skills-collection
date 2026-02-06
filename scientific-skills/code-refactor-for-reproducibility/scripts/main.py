#!/usr/bin/env python3
"""
Code Refactor for Reproducibility
=================================
将生物学家写的杂乱R/Python脚本重构为模块化、可复现的代码。

符合Nature/Science等顶级期刊对代码开源的要求。

Usage:
    python main.py --input /path/to/messy_scripts --output /path/to/refactored --language python --template nature
"""

import argparse
import ast
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class CodeAnalyzer:
    """代码分析器：解析原始脚本结构"""
    
    def __init__(self, language: str):
        self.language = language.lower()
        self.functions = []
        self.imports = []
        self.global_vars = []
        self.data_files = []
        
    def analyze_file(self, filepath: Path) -> Dict:
        """分析单个文件的结构"""
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        
        if self.language == 'python':
            return self._analyze_python(content, filepath)
        elif self.language == 'r':
            return self._analyze_r(content, filepath)
        else:
            raise ValueError(f"Unsupported language: {self.language}")
    
    def _analyze_python(self, content: str, filepath: Path) -> Dict:
        """解析Python代码"""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {'error': f'Syntax error: {e}', 'filepath': str(filepath)}
        
        functions = []
        imports = []
        classes = []
        global_vars = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'lineno': node.lineno,
                    'docstring': ast.get_docstring(node)
                }
                functions.append(func_info)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}")
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        # 检测数据文件引用
        data_patterns = [
            r'["\'](.+\.(csv|tsv|txt|fasta|fastq|json|xlsx|h5ad|rds|h5))["\']',
            r'pd\.read_(csv|excel|table)\(["\'](.+?)["\']',
            r'read\.csv\(["\'](.+?)["\']',
        ]
        for pattern in data_patterns:
            matches = re.findall(pattern, content)
            if matches:
                self.data_files.extend(matches)
        
        return {
            'filepath': str(filepath),
            'functions': functions,
            'imports': list(set(imports)),
            'classes': classes,
            'global_vars': global_vars,
            'data_files': self.data_files,
            'line_count': len(content.splitlines())
        }
    
    def _analyze_r(self, content: str, filepath: Path) -> Dict:
        """解析R代码"""
        functions = []
        imports = []
        
        # 提取函数定义
        func_pattern = r'(\w+)\s*\u003c-\s*function\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, content):
            functions.append({
                'name': match.group(1),
                'args': [a.strip() for a in match.group(2).split(',') if a.strip()]
            })
        
        # 提取library/require
        lib_pattern = r'(?:library|require)\(["\']?(\w+)["\']?\)'
        imports = re.findall(lib_pattern, content)
        
        # 检测数据文件
        data_patterns = [
            r'read\.(csv|tsv|table|RDS|rds)\(["\'](.+?)["\']',
            r'load\(["\'](.+?)["\']',
            r'\.\/(\w+\.\w+)',
        ]
        for pattern in data_patterns:
            matches = re.findall(pattern, content)
            if matches:
                self.data_files.extend(matches)
        
        return {
            'filepath': str(filepath),
            'functions': functions,
            'imports': list(set(imports)),
            'line_count': len(content.splitlines())
        }


class ProjectTemplate:
    """项目模板生成器"""
    
    TEMPLATES = {
        'nature': {
            'license': 'MIT',
            'requires_doi': True,
            'documentation_level': 'comprehensive',
            'required_files': ['README.md', 'LICENSE', 'CITATION.cff', 'environment.yml']
        },
        'science': {
            'license': 'Apache-2.0',
            'requires_doi': True,
            'documentation_level': 'comprehensive',
            'required_files': ['README.md', 'LICENSE', 'environment.yml', 'INSTALL.md']
        },
        'elife': {
            'license': 'MIT',
            'requires_doi': False,
            'documentation_level': 'standard',
            'required_files': ['README.md', 'LICENSE', 'requirements.txt']
        }
    }
    
    def __init__(self, template: str, language: str, project_name: str):
        self.template = template
        self.language = language
        self.project_name = project_name
        self.config = self.TEMPLATES.get(template, self.TEMPLATES['nature'])
    
    def generate_structure(self, output_dir: Path, analysis_results: List[Dict]):
        """生成项目结构"""
        # 创建目录
        dirs = ['src', 'tests', 'data/raw', 'data/processed', 'results', 'docs', 'notebooks']
        for d in dirs:
            (output_dir / d).mkdir(parents=True, exist_ok=True)
        
        # 生成文件
        self._generate_readme(output_dir, analysis_results)
        self._generate_license(output_dir)
        self._generate_citation(output_dir)
        self._generate_environment(output_dir)
        self._generate_src_init(output_dir)
        self._generate_data_loading(output_dir, analysis_results)
        self._generate_analysis_module(output_dir, analysis_results)
        self._generate_utils(output_dir)
        self._generate_main_script(output_dir, analysis_results)
        self._generate_tests(output_dir)
        self._generate_dockerfile(output_dir)
        self._generate_github_actions(output_dir)
    
    def _generate_readme(self, output_dir: Path, analysis_results: List[Dict]):
        """生成README.md"""
        today = datetime.now().strftime('%Y-%m-%d')
        total_lines = sum(r.get('line_count', 0) for r in analysis_results)
        
        content = f"""# {self.project_name}

[![License: {self.config['license']}](https://img.shields.io/badge/License-{self.config['license']}-blue.svg)]
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)]

## Overview

This repository contains reproducible analysis code for [Project Description].

- **Date**: {today}
- **Language**: {self.language.capitalize()}
- **Original lines**: {total_lines}
- **Template**: {self.template.capitalize()} Portfolio Standards

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/username/{self.project_name}.git
cd {self.project_name}

# Create environment (conda)
conda env create -f environment.yml
conda activate {self.project_name}

# Or use pip
pip install -r requirements.txt
```

### Usage

```bash
# Run main analysis
python src/main.py --config config.yaml

# Run tests
pytest tests/
```

## Project Structure

```
.
├── src/              # Source code
├── tests/            # Unit tests
├── data/             # Data directory
│   ├── raw/          # Original data
│   └── processed/    # Processed data
├── results/          # Output figures and tables
├── notebooks/        # Jupyter notebooks for exploration
└── docs/             # Additional documentation
```

## Data

- Raw data location: `data/raw/`
- Processed data: `data/processed/`
- **Note**: Large data files are not tracked in git (see `.gitignore`)

## Dependencies

See `environment.yml` (conda) or `requirements.txt` (pip) for full list.

Key dependencies:
- Python >= 3.9
- pandas, numpy, scipy
- matplotlib, seaborn
- scikit-learn

## Citation

If you use this code, please cite:

```
[Your Citation Here]
```

## License

This project is licensed under the {self.config['license']} License - see [LICENSE](LICENSE) for details.

## Contact

- [Your Name](mailto:email@institution.edu)
- [Issue Tracker](https://github.com/username/{self.project_name}/issues)
"""
        (output_dir / 'README.md').write_text(content)
    
    def _generate_license(self, output_dir: Path):
        """生成LICENSE文件"""
        year = datetime.now().year
        if self.config['license'] == 'MIT':
            content = f"""MIT License

Copyright (c) {year} [Author Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        else:  # Apache-2.0
            content = f"""Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright (c) {year} [Author Name]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
        (output_dir / 'LICENSE').write_text(content)
    
    def _generate_citation(self, output_dir: Path):
        """生成CITATION.cff"""
        content = f"""cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: "{self.project_name}"
authors:
  - family-names: "[Last Name]"
    given-names: "[First Name]"
    orcid: "https://orcid.org/0000-0000-0000-0000"
date-released: {datetime.now().strftime('%Y-%m-%d')}
version: "1.0.0"
repository-code: "https://github.com/username/{self.project_name}"
license: {self.config['license']}
type: software
"""
        (output_dir / 'CITATION.cff').write_text(content)
    
    def _generate_environment(self, output_dir: Path):
        """生成环境配置文件"""
        # environment.yml
        env_content = f"""name: {self.project_name}
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - python=3.10
  - pip
  - numpy=1.24
  - pandas=2.0
  - scipy=1.11
  - matplotlib=3.7
  - seaborn=0.12
  - scikit-learn=1.3
  - jupyter
  - pytest
  - black
  - ruff
  - mypy
  - pip:
    - -r requirements.txt
"""
        (output_dir / 'environment.yml').write_text(env_content)
        
        # requirements.txt
        req_content = """# Core dependencies
numpy==1.24.3
pandas==2.0.3
scipy==1.11.1

# Visualization
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0

# Machine Learning
scikit-learn==1.3.0

# Utilities
pyyaml==6.0.1
tqdm==4.65.0

# Development
pytest==7.4.0
black==23.7.0
ruff==0.0.280
mypy==1.4.1
"""
        (output_dir / 'requirements.txt').write_text(req_content)
    
    def _generate_src_init(self, output_dir: Path):
        """生成src/__init__.py"""
        content = '''"""
{project_name} Analysis Package

A reproducible analysis pipeline.
"""

__version__ = "1.0.0"
__author__ = "[Author Name]"

from .data_loading import load_data, validate_data
from .analysis import run_analysis
from .utils import setup_logging, set_random_seed

__all__ = [
    "load_data",
    "validate_data", 
    "run_analysis",
    "setup_logging",
    "set_random_seed",
]
'''.format(project_name=self.project_name)
        
        src_dir = output_dir / 'src'
        src_dir.mkdir(exist_ok=True)
        (src_dir / '__init__.py').write_text(content)
    
    def _generate_data_loading(self, output_dir: Path, analysis_results: List[Dict]):
        """生成数据加载模块"""
        content = '''"""Data loading and validation module.

This module handles all data input operations with validation
and reproducibility guarantees.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def load_data(
    filepath: Union[str, Path],
    file_format: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """Load data from various formats with validation.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the data file
    file_format : str, optional
        File format (csv, tsv, excel, etc.). Auto-detected if None.
    **kwargs
        Additional arguments passed to pandas read function
    
    Returns
    -------
    pd.DataFrame
        Loaded and validated data
    
    Raises
    ------
    FileNotFoundError
        If file does not exist
    ValueError
        If file format is not supported
    
    Examples
    --------
    >>> df = load_data("data/raw/expression.csv")
    >>> df = load_data("data.xlsx", sheet_name="Sheet1")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    # Auto-detect format
    if file_format is None:
        file_format = filepath.suffix.lower().lstrip('.')
    
    logger.info(f"Loading data from {filepath} (format: {file_format})")
    
    # Dispatch to appropriate loader
    loaders = {
        'csv': pd.read_csv,
        'tsv': lambda f, **kw: pd.read_csv(f, sep='\t', **kw),
        'txt': lambda f, **kw: pd.read_csv(f, sep='\t', **kw),
        'xlsx': pd.read_excel,
        'xls': pd.read_excel,
        'json': pd.read_json,
    }
    
    if file_format not in loaders:
        raise ValueError(f"Unsupported format: {file_format}")
    
    df = loaders[file_format](filepath, **kwargs)
    
    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    
    return df


def validate_data(
    df: pd.DataFrame,
    required_columns: Optional[list] = None,
    check_missing: bool = True,
    check_duplicates: bool = True
) -> Dict[str, Any]:
    """Validate data quality and structure.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data to validate
    required_columns : list, optional
        List of required column names
    check_missing : bool
        Whether to check for missing values
    check_duplicates : bool
        Whether to check for duplicate rows
    
    Returns
    -------
    dict
        Validation report with metrics and flags
    """
    report = {
        'n_rows': len(df),
        'n_columns': len(df.columns),
        'columns': list(df.columns),
        'valid': True,
        'issues': []
    }
    
    # Check required columns
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            report['valid'] = False
            report['issues'].append(f"Missing columns: {missing}")
    
    # Check missing values
    if check_missing:
        missing_pct = df.isnull().sum() / len(df) * 100
        if missing_pct.any():
            report['missing_percent'] = missing_pct[missing_pct > 0].to_dict()
            logger.warning(f"Found missing values in columns: {report['missing_percent']}")
    
    # Check duplicates
    if check_duplicates:
        n_dups = df.duplicated().sum()
        report['n_duplicates'] = n_dups
        if n_dups > 0:
            report['issues'].append(f"Found {n_dups} duplicate rows")
    
    return report


def save_processed_data(
    df: pd.DataFrame,
    output_path: Union[str, Path],
    metadata: Optional[Dict] = None
) -> None:
    """Save processed data with metadata.
    
    Parameters
    ----------
    df : pd.DataFrame
        Processed data to save
    output_path : str or Path
        Output file path
    metadata : dict, optional
        Metadata to include in output
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save data
    if output_path.suffix == '.csv':
        df.to_csv(output_path, index=False)
    elif output_path.suffix in ['.xlsx', '.xls']:
        df.to_excel(output_path, index=False)
    else:
        df.to_csv(output_path, index=False)
    
    # Save metadata if provided
    if metadata:
        import json
        meta_path = output_path.with_suffix('.metadata.json')
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    logger.info(f"Saved processed data to {output_path}")
'''
        (output_dir / 'src' / 'data_loading.py').write_text(content)
    
    def _generate_analysis_module(self, output_dir: Path, analysis_results: List[Dict]):
        """生成分析模块"""
        # 提取原始函数名用于重构
        all_functions = []
        for result in analysis_results:
            all_functions.extend(result.get('functions', []))
        
        content = '''"""Analysis module.

Core analysis functions for the project.
All functions include reproducibility guarantees (fixed seeds, etc.)
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from .utils import set_random_seed

logger = logging.getLogger(__name__)


def run_analysis(
    data: pd.DataFrame,
    config: Optional[Dict] = None,
    random_seed: int = 42
) -> Dict[str, Any]:
    """Run the complete analysis pipeline.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data for analysis
    config : dict, optional
        Analysis configuration parameters
    random_seed : int
        Random seed for reproducibility
    
    Returns
    -------
    dict
        Analysis results
    """
    # Set seed for reproducibility
    set_random_seed(random_seed)
    
    logger.info("Starting analysis pipeline")
    
    results = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'random_seed': random_seed,
        'config': config or {},
    }
    
    # TODO: Add your analysis steps here
    # Example structure:
    # results['preprocessing'] = preprocess_data(data, config)
    # results['statistics'] = compute_statistics(data)
    # results['models'] = fit_models(data, config)
    
    logger.info("Analysis complete")
    return results


def compute_statistics(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """Compute descriptive statistics.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data
    columns : list, optional
        Specific columns to analyze (all numeric if None)
    
    Returns
    -------
    pd.DataFrame
        Statistics summary
    """
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    
    stats_df = data[columns].describe()
    
    # Add additional statistics
    stats_df.loc['skew'] = data[columns].skew()
    stats_df.loc['kurtosis'] = data[columns].kurtosis()
    
    return stats_df


def correlation_analysis(
    data: pd.DataFrame,
    method: str = 'pearson'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Perform correlation analysis.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data (numeric columns only)
    method : str
        Correlation method ('pearson', 'spearman', 'kendall')
    
    Returns
    -------
    tuple
        (correlation matrix, p-value matrix)
    """
    numeric_data = data.select_dtypes(include=[np.number])
    
    corr_matrix = numeric_data.corr(method=method)
    
    # Compute p-values
    pvalue_matrix = pd.DataFrame(
        np.zeros_like(corr_matrix),
        index=corr_matrix.index,
        columns=corr_matrix.columns
    )
    
    for i, col1 in enumerate(corr_matrix.columns):
        for j, col2 in enumerate(corr_matrix.columns):
            if i != j:
                _, pval = stats.pearsonr(
                    numeric_data[col1].dropna(),
                    numeric_data[col2].dropna()
                )
                pvalue_matrix.iloc[i, j] = pval
    
    return corr_matrix, pvalue_matrix


# TODO: Add your analysis functions here
# Copy and refactor functions from original scripts
'''
        (output_dir / 'src' / 'analysis.py').write_text(content)
    
    def _generate_utils(self, output_dir: Path):
        """生成工具模块"""
        content = '''"""Utility functions.

Common utilities for logging, random seed management,
and reproducibility.
"""

import logging
import os
import random
import sys
from pathlib import Path
from typing import Optional

import numpy as np


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_str: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration.
    
    Parameters
    ----------
    level : int
        Logging level (default: INFO)
    log_file : str, optional
        Path to log file (console only if None)
    format_str : str, optional
        Custom format string
    
    Returns
    -------
    logging.Logger
        Configured logger
    """
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=handlers,
        force=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized")
    
    return logger


def set_random_seed(seed: int = 42) -> None:
    """Set random seeds for reproducibility.
    
    Sets seeds for Python random, numpy, and other libraries.
    
    Parameters
    ----------
    seed : int
        Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    
    # Try to set seeds for optional libraries
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass
    
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except ImportError:
        pass
    
    logging.getLogger(__name__).info(f"Random seed set to {seed}")


def ensure_dir(path: str) -> Path:
    """Ensure directory exists.
    
    Parameters
    ----------
    path : str
        Directory path
    
    Returns
    -------
    Path
        Path object for directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_project_root() -> Path:
    """Get project root directory.
    
    Returns
    -------
    Path
        Project root directory
    """
    # Assumes this file is in src/
    return Path(__file__).parent.parent


def save_reproducibility_info(output_dir: str) -> None:
    """Save system and environment info for reproducibility.
    
    Parameters
    ----------
    output_dir : str
        Directory to save info
    """
    import json
    import platform
    import subprocess
    
    info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'hostname': platform.node(),
    }
    
    # Try to get package versions
    try:
        result = subprocess.run(
            ['pip', 'freeze'],
            capture_output=True,
            text=True
        )
        info['packages'] = result.stdout.strip().split('\n')
    except Exception:
        info['packages'] = []
    
    output_path = Path(output_dir) / 'reproducibility_info.json'
    with open(output_path, 'w') as f:
        json.dump(info, f, indent=2)
    
    logging.getLogger(__name__).info(f"Saved reproducibility info to {output_path}")
'''
        (output_dir / 'src' / 'utils.py').write_text(content)
    
    def _generate_main_script(self, output_dir: Path, analysis_results: List[Dict]):
        """生成主执行脚本"""
        content = '''#!/usr/bin/env python3
"""Main analysis script.

Entry point for running the complete analysis pipeline.
"""

import argparse
import logging
from pathlib import Path

from src.data_loading import load_data, save_processed_data, validate_data
from src.analysis import run_analysis
from src.utils import ensure_dir, save_reproducibility_info, setup_logging

logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run reproducible analysis pipeline"
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Path to input data file'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='results',
        help='Output directory (default: results)'
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level, log_file=f"{args.output}/analysis.log")
    
    logger.info("="*50)
    logger.info("Starting Analysis Pipeline")
    logger.info("="*50)
    
    # Create output directory
    output_dir = ensure_dir(args.output)
    
    # Load configuration if provided
    config = {}
    if args.config:
        import yaml
        with open(args.config) as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {args.config}")
    
    # Load data
    logger.info(f"Loading data from {args.input}")
    data = load_data(args.input)
    
    # Validate data
    validation = validate_data(data)
    if not validation['valid']:
        logger.error(f"Data validation failed: {validation['issues']}")
        raise ValueError("Data validation failed")
    
    logger.info(f"Data loaded: {validation['n_rows']} rows, {validation['n_columns']} columns")
    
    # Run analysis
    results = run_analysis(data, config=config, random_seed=args.seed)
    
    # Save reproducibility info
    save_reproducibility_info(output_dir)
    
    logger.info("Analysis complete!")
    logger.info(f"Results saved to {output_dir}")


if __name__ == '__main__':
    main()
'''
        (output_dir / 'src' / 'main.py').write_text(content)
        # Make executable
        os.chmod(output_dir / 'src' / 'main.py', 0o755)
    
    def _generate_tests(self, output_dir: Path):
        """生成测试文件"""
        # tests/__init__.py
        (output_dir / 'tests' / '__init__.py').touch()
        
        # tests/test_data_loading.py
        test_content = '''"""Tests for data loading module."""

import pytest
import pandas as pd
from pathlib import Path

from src.data_loading import load_data, validate_data


class TestLoadData:
    """Test data loading functions."""
    
    def test_load_csv(self, tmp_path):
        """Test loading CSV file."""
        # Create test file
        test_file = tmp_path / "test.csv"
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        df.to_csv(test_file, index=False)
        
        # Load and verify
        result = load_data(test_file)
        assert len(result) == 2
        assert list(result.columns) == ['a', 'b']
    
    def test_file_not_found(self):
        """Test error on missing file."""
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent.csv")
    
    def test_unsupported_format(self, tmp_path):
        """Test error on unsupported format."""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("content")
        
        with pytest.raises(ValueError):
            load_data(test_file)


class TestValidateData:
    """Test data validation functions."""
    
    def test_valid_data(self):
        """Test validation of clean data."""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        result = validate_data(df)
        
        assert result['valid'] is True
        assert result['n_rows'] == 3
        assert result['n_columns'] == 2
    
    def test_missing_required_columns(self):
        """Test validation with missing required columns."""
        df = pd.DataFrame({'a': [1, 2]})
        result = validate_data(df, required_columns=['a', 'b', 'c'])
        
        assert result['valid'] is False
        assert len(result['issues']) > 0
    
    def test_detects_duplicates(self):
        """Test detection of duplicate rows."""
        df = pd.DataFrame({'a': [1, 1], 'b': [2, 2]})
        result = validate_data(df, check_duplicates=True)
        
        assert result['n_duplicates'] == 1
'''
        (output_dir / 'tests' / 'test_data_loading.py').write_text(test_content)
        
        # tests/test_analysis.py
        test_analysis = '''"""Tests for analysis module."""

import numpy as np
import pandas as pd
import pytest

from src.analysis import compute_statistics, correlation_analysis


class TestComputeStatistics:
    """Test statistics computation."""
    
    def test_basic_stats(self):
        """Test basic statistics calculation."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [10, 20, 30, 40, 50]
        })
        
        stats = compute_statistics(df)
        
        assert 'mean' in stats.index
        assert 'std' in stats.index
        assert 'skew' in stats.index
    
    def test_column_selection(self):
        """Test selecting specific columns."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': ['x', 'y', 'z']  # non-numeric
        })
        
        stats = compute_statistics(df, columns=['a', 'b'])
        
        assert list(stats.columns) == ['a', 'b']


class TestCorrelationAnalysis:
    """Test correlation analysis."""
    
    def test_correlation_matrix(self):
        """Test correlation matrix computation."""
        np.random.seed(42)
        df = pd.DataFrame({
            'a': np.random.randn(100),
            'b': np.random.randn(100),
            'c': np.random.randn(100)
        })
        
        corr, pval = correlation_analysis(df, method='pearson')
        
        assert corr.shape == (3, 3)
        assert pval.shape == (3, 3)
        assert np.allclose(np.diag(corr), 1.0)
'''
        (output_dir / 'tests' / 'test_analysis.py').write_text(test_analysis)
        
        # pytest.ini
        pytest_ini = '''[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
'''
        (output_dir / 'pytest.ini').write_text(pytest_ini)
    
    def _generate_dockerfile(self, output_dir: Path):
        """生成Dockerfile"""
        content = '''# Dockerfile for reproducible analysis
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY data/ ./data/

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command
CMD ["python", "src/main.py", "--help"]
'''
        (output_dir / 'Dockerfile').write_text(content)
    
    def _generate_github_actions(self, output_dir: Path):
        """生成GitHub Actions配置"""
        workflow_dir = output_dir / '.github' / 'workflows'
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        content = '''name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with ruff
      run: |
        pip install ruff
        ruff check src/ tests/
    
    - name: Format check with black
      run: |
        pip install black
        black --check src/ tests/
    
    - name: Run tests
      run: |
        pytest tests/ -v --tb=short
'''
        (workflow_dir / 'tests.yml').write_text(content)
        
        # .gitignore
        gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Data (large files)
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Results
results/*
!results/.gitkeep

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
'''
        (output_dir / '.gitignore').write_text(gitignore)
        
        # Add .gitkeep files
        (output_dir / 'data' / 'raw' / '.gitkeep').touch()
        (output_dir / 'data' / 'processed' / '.gitkeep').touch()
        (output_dir / 'results' / '.gitkeep').touch()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Refactor messy scripts into reproducible, journal-compliant code"
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Path to original scripts directory'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        required=True,
        help='Path to output directory'
    )
    parser.add_argument(
        '--language', '-l',
        choices=['python', 'r'],
        default='python',
        help='Programming language (default: python)'
    )
    parser.add_argument(
        '--template', '-t',
        choices=['nature', 'science', 'elife'],
        default='nature',
        help='Journal template (default: nature)'
    )
    parser.add_argument(
        '--project-name', '-n',
        type=str,
        help='Project name (default: output folder name)'
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine project name
    project_name = args.project_name or output_dir.name
    
    print(f"🔬 Code Refactor for Reproducibility")
    print(f"=" * 50)
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Language: {args.language}")
    print(f"Template: {args.template}")
    print(f"Project:  {project_name}")
    print()
    
    # Analyze existing code
    print("📊 Analyzing original scripts...")
    analyzer = CodeAnalyzer(args.language)
    analysis_results = []
    
    if args.language == 'python':
        extensions = ['.py', '.ipynb']
    else:
        extensions = ['.R', '.r']
    
    for ext in extensions:
        for filepath in input_dir.rglob(f'*{ext}'):
            if '__pycache__' not in str(filepath):
                result = analyzer.analyze_file(filepath)
                analysis_results.append(result)
                print(f"  ✓ Analyzed: {filepath.name} ({result.get('line_count', 0)} lines, {len(result.get('functions', []))} functions)")
    
    if not analysis_results:
        print("  ⚠ No source files found in input directory")
    
    print()
    
    # Generate project structure
    print("🏗️  Generating project structure...")
    template = ProjectTemplate(args.template, args.language, project_name)
    template.generate_structure(output_dir, analysis_results)
    
    print("  ✓ Created src/ - Source code modules")
    print("  ✓ Created tests/ - Unit tests")
    print("  ✓ Created data/ - Data directory structure")
    print("  ✓ Created docs/ - Documentation")
    print("  ✓ Created configuration files")
    print()
    
    # Summary
    print("=" * 50)
    print("✅ Refactoring complete!")
    print()
    print("Next steps:")
    print(f"  1. cd {output_dir}")
    print("  2. Review README.md and update project description")
    print("  3. Copy original functions to appropriate modules in src/")
    print("  4. Update CITATION.cff with author information")
    print("  5. Run tests: pytest tests/")
    print("  6. Initialize git: git init && git add . && git commit -m 'Initial commit'")
    print()
    print("📖 For Nature/Science compliance:")
    print("  - Archive on Zenodo/Figshare for DOI")
    print("  - Ensure LICENSE matches journal requirements")
    print("  - Add detailed analysis notebook to notebooks/")


if __name__ == '__main__':
    main()
