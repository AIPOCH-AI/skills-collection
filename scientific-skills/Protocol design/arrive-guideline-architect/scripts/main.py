#!/usr/bin/env python3
"""
ARRIVE Guideline Architect
Design impeccable animal experiment protocols based on ARRIVE 2.0 standards

Usage:
    python main.py --interactive          # Interactive experiment design
    python main.py --input file.json      # Generate protocol from input file
    python main.py --validate file.md     # Validate existing protocol compliance
    python main.py --checklist            # Generate ARRIVE checklist
"""

import argparse
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ARRIVEGuidelineArchitect:
    """ARRIVE 2.0 Protocol Architect"""
    
    # ARRIVE 2.0 Essential 10 Checklist Items
    ESSENTIAL_10 = {
        "1. Study Design": {
            "description": "For each experiment, provide brief details of study design including: the number of experimental and control groups; the number of animals per group; and a clear statement of whether the experiment was performed blinded.",
            "checkpoints": [
                "Specify number of experimental and control groups",
                "Specify number of animals per group",
                "Indicate whether blinding was used"
            ]
        },
        "2. Sample Size": {
            "description": "Provide details of sample size calculation, including: the effect size of interest; the estimate of variability; the power; and the significance level.",
            "checkpoints": [
                "Effect size estimate",
                "Variability estimate",
                "Power (usually ≥80%)",
                "Significance level (usually α=0.05)"
            ]
        },
        "3. Inclusion/Exclusion Criteria": {
            "description": "Provide details of inclusion and exclusion criteria for experimental units, including handling of any data exclusions.",
            "checkpoints": [
                "Clear inclusion criteria",
                "Clear exclusion criteria",
                "Handling of data exclusions"
            ]
        },
        "4. Randomisation": {
            "description": "Provide details of: the randomisation method used to allocate experimental units to groups; and the randomisation method used to determine the order of treatments and measurements.",
            "checkpoints": [
                "Group randomization method",
                "Randomization method for treatment and measurement order",
                "Randomization implementation details"
            ]
        },
        "5. Blinding": {
            "description": "Describe who was aware of group allocation at the different stages of the experiment (during the allocation, the conduct of the experiment, the outcome assessment, and the data analysis).",
            "checkpoints": [
                "Group allocation stage: who was aware",
                "Experiment conduct stage: who was aware",
                "Outcome assessment stage: who was aware",
                "Data analysis stage: who was aware"
            ]
        },
        "6. Outcome Measures": {
            "description": "Define all outcome measures assessed (primary and secondary), clearly distinguishing between measures assessed as part of the experimental protocol and measures assessed in exploratory analyses.",
            "checkpoints": [
                "Primary outcome measure definition",
                "Secondary outcome measure definition",
                "Distinguish between pre-specified and exploratory analyses"
            ]
        },
        "7. Statistical Methods": {
            "description": "Describe in full how the data were analysed, including all statistical methods applied to the data; and whether assumptions of the statistical approaches were met.",
            "checkpoints": [
                "Complete statistical method description",
                "Assumption validation for hypothesis testing",
                "Multiple comparison correction method"
            ]
        },
        "8. Experimental Animals": {
            "description": "Provide full details of the animals used, including: species and strain; sex; age or developmental stage; weight or mass; source (including supplier or breeding centre); and any relevant welfare and housing details.",
            "checkpoints": [
                "Species and strain",
                "Sex",
                "Age or developmental stage",
                "Weight/mass",
                "Source (supplier or breeding center)",
                "Housing conditions and welfare"
            ]
        },
        "9. Experimental Procedures": {
            "description": "Provide full details of all procedures carried out on the animals, including: what was done, how it was done, and what was used.",
            "checkpoints": [
                "Detailed operational steps",
                "Methods and tools used",
                "Anesthesia and analgesia methods",
                "Sample collection methods"
            ]
        },
        "10. Results": {
            "description": "Report the results for each analysis carried out, with a measure of precision (e.g., standard error or confidence interval), and include the exact number of experimental units analysed in each group.",
            "checkpoints": [
                "Exact values per group (to the individual level)",
                "Variability metrics (SD/SEM/CI)",
                "Statistics and P-values",
                "Effect size and confidence intervals"
            ]
        }
    }
    
    # Recommended Set
    RECOMMENDED_SET = {
        "11. Ethical Approval": "Provide ethical approval information, including institutional ethics committee name and approval number",
        "12. Housing and Husbandry": "Detailed housing conditions (temperature, humidity, light cycle, housing density, etc.)",
        "13. Animal Care and Monitoring": "Animal care and monitoring frequency, humane endpoint settings",
        "14. Adverse Events": "Definition, monitoring, and handling of adverse events",
        "15. Data Access": "Data sharing and accessibility statement",
        "16. Conflicts of Interest": "Conflict of interest statement",
        "17. Funding": "Funding source statement",
        "18. Limitations": "Research limitations statement"
    }
    
    # Common Animal Experiment Type Templates
    STUDY_TEMPLATES = {
        "efficacy": {
            "name": "Efficacy Study",
            "description": "Evaluate drug or treatment efficacy in animal models",
            "typical_groups": ["Sham group", "Model control group", "Positive control group", "Low dose group", "Medium dose group", "High dose group"],
            "typical_endpoints": ["Disease activity score", "Biomarkers", "Histopathological score"]
        },
        "toxicology": {
            "name": "Toxicology Study",
            "description": "Evaluate safety profile of compounds",
            "typical_groups": ["Vehicle control group", "Low dose group", "Medium dose group", "High dose group"],
            "typical_endpoints": ["Body weight", "Hematology indicators", "Clinical biochemistry", "Organ weight", "Histopathology"]
        },
        "pharmacokinetics": {
            "name": "PK Study",
            "description": "Evaluate drug absorption, distribution, metabolism, and excretion",
            "typical_groups": ["IV administration group", "Oral administration group"],
            "typical_endpoints": ["Cmax", "Tmax", "AUC", "Half-life", "Clearance"]
        },
        "behavioral": {
            "name": "Behavioral Study",
            "description": "Evaluate animal behavior changes",
            "typical_groups": ["Control group", "Model group", "Treatment group"],
            "typical_endpoints": ["Motor ability", "Learning and memory", "Anxiety-like behavior", "Depression-like behavior"]
        }
    }
    
    def __init__(self):
        self.protocol_data = {}
    
    def interactive_design(self) -> Dict[str, Any]:
        """Interactive experiment design wizard"""
        print("=" * 70)
        print("🧬 ARRIVE Guideline Architect - Interactive Animal Experiment Design Wizard")
        print("=" * 70)
        print("\nThis wizard will help you design animal experiment protocols compliant with ARRIVE 2.0 standards.\n")
        
        data = {}
        
        # Basic Information
        print("【Step 1】Basic Information")
        print("-" * 40)
        data['title'] = input("Study title: ").strip()
        
        print("\nExperiment type selection:")
        for key, template in self.STUDY_TEMPLATES.items():
            print(f"  [{key}] {template['name']}: {template['description']}")
        
        study_type = input("\nPlease select experiment type (default: efficacy): ").strip() or "efficacy"
        data['study_type'] = study_type
        
        # Animal Information
        print("\n【Step 2】Experimental Animal Information (Item 8)")
        print("-" * 40)
        data['species'] = input("Species (e.g., Mus musculus): ").strip() or "Mus musculus"
        data['strain'] = input("Strain (e.g., C57BL/6J): ").strip()
        data['sex'] = input("Sex (Male/Female/Both): ").strip() or "Male"
        data['age'] = input("Age/weeks (e.g., 8-10 weeks): ").strip() or "8-10 weeks"
        data['weight_range'] = input("Weight range (e.g., 20-25g): ").strip() or "20-25g"
        data['source'] = input("Animal source (supplier or breeding center): ").strip() or "SPF-grade animal center"
        
        # Experimental Design
        print("\n【Step 3】Experimental Design (Items 1, 2)")
        print("-" * 40)
        
        print("Experimental group setup:")
        groups = []
        group_count = int(input("Number of experimental groups (including control): ").strip() or "3")
        
        for i in range(group_count):
            group_name = input(f"  Group {i+1} name: ").strip()
            treatment = input(f"  Group {i+1} treatment: ").strip()
            groups.append({"name": group_name, "treatment": treatment})
        data['groups'] = groups
        
        # Sample Size
        sample_size = input(f"\nAnimals per group (default: 10): ").strip() or "10"
        data['sample_size_per_group'] = int(sample_size)
        data['total_animals'] = data['sample_size_per_group'] * len(groups)
        
        print("\nSample size calculation basis:")
        data['effect_size'] = input("  Expected effect size (e.g., 0.8): ").strip() or "0.8"
        data['power'] = input("  Statistical power (default: 0.80): ").strip() or "0.80"
        data['alpha'] = input("  Significance level α (default: 0.05): ").strip() or "0.05"
        
        # Randomization and Blinding
        print("\n【Step 4】Randomization and Blinding (Items 4, 5)")
        print("-" * 40)
        data['randomization_method'] = input(
            "Randomization method (e.g., computer random number table/random number generator): ").strip() or "Computer random number generator"
        data['blinding'] = input("Use blinding (Yes/No): ").strip() or "Yes"
        if data['blinding'].lower() == 'yes':
            data['blinding_details'] = input("Blinding implementation details (who, when, how): ").strip() or "Both experiment operators and outcome assessors were blinded to group allocation"
        
        # Outcome Measures
        print("\n【Step 5】Outcome Measures (Item 6)")
        print("-" * 40)
        data['primary_endpoint'] = input("Primary outcome measure: ").strip()
        
        secondary = input("Secondary outcome measures (comma-separated): ").strip()
        data['secondary_endpoints'] = [s.strip() for s in secondary.split(",") if s.strip()]
        
        # Statistical Analysis
        print("\n【Step 6】Statistical Methods (Item 7)")
        print("-" * 40)
        data['statistical_method'] = input(
            "Main statistical method (e.g., One-way ANOVA + Tukey's post-hoc): ").strip() or "One-way ANOVA"
        
        # Experimental Procedures
        print("\n【Step 7】Experimental Procedures (Item 9)")
        print("-" * 40)
        data['study_duration'] = input("Study duration (days): ").strip()
        data['dosing_route'] = input("Dosing route (e.g., oral gavage/IP injection/IV injection): ").strip() or "Oral gavage"
        data['dosing_frequency'] = input("Dosing frequency (e.g., once daily/three times weekly): ").strip() or "Once daily"
        
        # Ethics
        print("\n【Step 8】Ethics and Welfare")
        print("-" * 40)
        data['ethical_approval'] = input("Ethics committee name: ").strip()
        data['approval_number'] = input("Approval number: ").strip()
        data['housing_conditions'] = input("Housing conditions (e.g., SPF-grade, temperature 22±2°C, humidity 50±10%): ").strip() or "SPF-grade environment"
        
        self.protocol_data = data
        return data
    
    def generate_protocol(self, data: Optional[Dict] = None, output_format: str = "markdown") -> str:
        """Generate complete experiment protocol"""
        if data is None:
            data = self.protocol_data
        
        if output_format == "markdown":
            return self._generate_markdown_protocol(data)
        else:
            return self._generate_text_protocol(data)
    
    def _generate_markdown_protocol(self, data: Dict) -> str:
        """Generate Markdown format experiment protocol"""
        md = []
        
        # Title
        md.append(f"# {data.get('title', 'Animal Experiment Protocol')}")
        md.append(f"\n> This protocol is designed in strict accordance with ARRIVE 2.0 guidelines")
        md.append(f"> Generated date: {datetime.now().strftime('%Y-%m-%d')}\n")
        
        # 1. Study Design
        md.append("## 1. Study Design\n")
        md.append(f"**Experiment type**: {self.STUDY_TEMPLATES.get(data.get('study_type', 'efficacy'), {}).get('name', 'Custom study')}\n")
        md.append(f"**Number of groups**: {len(data.get('groups', []))}")
        md.append(f"**Animals per group**: {data.get('sample_size_per_group', 'N/A')}")
        md.append(f"**Total animals**: {data.get('total_animals', 'N/A')}\n")
        
        md.append("### Experimental Groups")
        md.append("| Group | Treatment | Animals |")
        md.append("|------|----------|--------|")
        for group in data.get('groups', []):
            md.append(f"| {group.get('name', 'N/A')} | {group.get('treatment', 'N/A')} | {data.get('sample_size_per_group', 'N/A')} |")
        md.append("")
        
        md.append(f"**Blinding**: {data.get('blinding', 'No')}")
        if data.get('blinding_details'):
            md.append(f"**Blinding details**: {data['blinding_details']}")
        md.append("")
        
        # 2. Sample Size
        md.append("## 2. Sample Size Calculation\n")
        md.append("Sample size calculated based on the following parameters:\n")
        md.append(f"- **Expected effect size**: {data.get('effect_size', 'N/A')}")
        md.append(f"- **Statistical power (1-β)**: {data.get('power', '0.80')}")
        md.append(f"- **Significance level (α)**: {data.get('alpha', '0.05')}")
        md.append(f"- **Final animals per group**: {data.get('sample_size_per_group', 'N/A')} (considering 10% dropout rate)\n")
        
        # 3. Inclusion/Exclusion
        md.append("## 3. Inclusion and Exclusion Criteria\n")
        md.append("### Inclusion Criteria")
        md.append(f"- Species: {data.get('species', 'N/A')}")
        md.append(f"- Strain: {data.get('strain', 'N/A')}")
        md.append(f"- Sex: {data.get('sex', 'N/A')}")
        md.append(f"- Age: {data.get('age', 'N/A')}")
        md.append(f"- Weight range: {data.get('weight_range', 'N/A')}")
        md.append("- Health status: No visible signs of disease\n")
        
        md.append("### Exclusion Criteria")
        md.append("- Abnormal health status before experiment")
        md.append("- Unexpected death during administration (requires autopsy)")
        md.append("- Failed sample collection\n")
        
        # 4. Randomisation
        md.append("## 4. Randomization Plan\n")
        md.append(f"**Randomization method**: {data.get('randomization_method', 'Computer random number generator')}")
        md.append("- Animals stratified by body weight and randomly assigned to groups")
        md.append("- Random numbers generated using SPSS/R/Python")
        md.append("- Randomization performed by personnel independent of experiment operators\n")
        
        # 5. Blinding
        md.append("## 5. Blinding\n")
        if data.get('blinding', 'No').lower() == 'yes':
            md.append("| Stage | Personnel Aware | Notes |")
            md.append("|------|-----------------|-------|")
            md.append("| Group allocation | Only randomization executor | Allocation scheme sealed and stored |")
            md.append("| Experiment operation | Operators blinded | Drug numbering used |")
            md.append("| Outcome assessment | Assessors blinded | Independent assessment |")
            md.append("| Data analysis | Analysts blinded | Analysis by group code |")
        else:
            md.append("This experiment uses an open-label design without blinding.")
        md.append("")
        
        # 6. Outcome Measures
        md.append("## 6. Outcome Measures\n")
        md.append(f"**Primary outcome measure**: {data.get('primary_endpoint', 'N/A')}")
        md.append("\n**Secondary outcome measures**:")
        for endpoint in data.get('secondary_endpoints', []):
            md.append(f"- {endpoint}")
        md.append("")
        
        # 7. Statistical Methods
        md.append("## 7. Statistical Methods\n")
        md.append(f"**Main analysis method**: {data.get('statistical_method', 'One-way ANOVA')}")
        md.append("- Normality test: Shapiro-Wilk test")
        md.append("- Homogeneity of variance test: Levene's test")
        md.append("- Multiple comparison correction: Tukey's HSD or Bonferroni")
        md.append("- Significance level: α = 0.05 (two-tailed)")
        md.append("- Software: GraphPad Prism 9.0 or SPSS 26.0\n")
        
        # 8. Experimental Animals
        md.append("## 8. Experimental Animals\n")
        md.append(f"| Parameter | Details |")
        md.append(f"|------|------|")
        md.append(f"| Species | {data.get('species', 'N/A')} |")
        md.append(f"| Strain | {data.get('strain', 'N/A')} |")
        md.append(f"| Sex | {data.get('sex', 'N/A')} |")
        md.append(f"| Age | {data.get('age', 'N/A')} |")
        md.append(f"| Weight | {data.get('weight_range', 'N/A')} |")
        md.append(f"| Source | {data.get('source', 'N/A')} |")
        md.append(f"| Housing conditions | {data.get('housing_conditions', 'SPF-grade')} |")
        md.append("")
        
        # 9. Experimental Procedures
        md.append("## 9. Experimental Procedures\n")
        md.append(f"**Study duration**: {data.get('study_duration', 'N/A')} days")
        md.append(f"**Dosing route**: {data.get('dosing_route', 'N/A')}")
        md.append(f"**Dosing frequency**: {data.get('dosing_frequency', 'N/A')}")
        md.append("**Sample collection**: Blood and tissue samples collected at study endpoints")
        md.append("**Euthanasia method**: CO₂ asphyxiation or excess pentobarbital sodium\n")
        
        md.append("### Experimental Workflow")
        md.append("```")
        md.append("Day 0: Animal acclimation → Random grouping → Baseline measurements")
        md.append("Day 1-28: Daily dosing → Body weight monitoring → Behavioral observation")
        md.append("Day 28: Terminal measurements → Sample collection → Euthanasia")
        md.append("```\n")
        
        # 10. Results (Template)
        md.append("## 10. Expected Results Report Template\n")
        md.append("_Note: This is a results report template to be completed after experiment_\n")
        md.append("### Primary Outcome Measure")
        md.append("| Group | N | Mean ± SD | 95% CI | P-value (vs Control) |")
        md.append("|------|---|-----------|--------|---------------|")
        for group in data.get('groups', []):
            md.append(f"| {group.get('name', 'N/A')} | | | | |")
        md.append("")
        
        md.append("### Statistical Analysis")
        md.append("- Normality test results: ")
        md.append("- ANOVA results: F(df1, df2) = _, P = _")
        md.append("- Post-hoc test results: ")
        md.append("- Effect size (Cohen's d): \n")
        
        # Additional Information
        md.append("## 11. Ethics and Welfare\n")
        md.append(f"**Ethics committee**: {data.get('ethical_approval', 'To be filled')}")
        md.append(f"**Approval number**: {data.get('approval_number', 'To be filled')}")
        md.append("**Animal welfare**: Experiment follows 3R principles to minimize animal pain and numbers")
        md.append("**Humane endpoints**: Body weight loss >20%, severe behavioral abnormalities, inability to eat or drink\n")
        
        # ARRIVE Checklist
        md.append("---\n")
        md.append("# ARRIVE 2.0 Compliance Checklist\n")
        md.append("| Item | Content | Completed | Page |")
        md.append("|------|------|----------|------|")
        for item, details in self.ESSENTIAL_10.items():
            md.append(f"| {item} | {details['description'][:50]}... | ☐ | |")
        md.append("")
        
        md.append("---\n*This protocol was automatically generated by ARRIVE Guideline Architect*")
        
        return "\n".join(md)
    
    def _generate_text_protocol(self, data: Dict) -> str:
        """Generate plain text format experiment protocol"""
        return self._generate_markdown_protocol(data).replace('#', '').replace('|', '').replace('-', '')
    
    def generate_checklist(self, format_type: str = "markdown") -> str:
        """Generate ARRIVE 2.0 checklist"""
        lines = []
        lines.append("# ARRIVE 2.0 Essential 10 Checklist\n")
        lines.append(f"Check date: {datetime.now().strftime('%Y-%m-%d')}\n")
        
        for item, details in self.ESSENTIAL_10.items():
            lines.append(f"## {item}")
            lines.append(f"Description: {details['description']}\n")
            lines.append("Checkpoints:")
            for checkpoint in details['checkpoints']:
                lines.append(f"  ☐ {checkpoint}")
            lines.append("")
        
        lines.append("\n# Recommended Set Checklist\n")
        for item, description in self.RECOMMENDED_SET.items():
            lines.append(f"## {item}")
            lines.append(f"  ☐ {description}\n")
        
        return "\n".join(lines)
    
    def validate_protocol(self, protocol_text: str) -> Dict[str, Any]:
        """Validate whether experiment protocol complies with ARRIVE 2.0 standards"""
        results = {
            "score": 0,
            "max_score": len(self.ESSENTIAL_10),
            "compliance": {},
            "recommendations": []
        }
        
        text_lower = protocol_text.lower()
        
        # Check Essential 10 items
        checks = {
            "1. Study Design": ["group", "design", "blind"],
            "2. Sample Size": ["sample size", "power", "effect size", "significance"],
            "3. Inclusion/Exclusion Criteria": ["inclusion", "exclusion", "criteria"],
            "4. Randomisation": ["random", "allocation"],
            "5. Blinding": ["blind", "mask"],
            "6. Outcome Measures": ["outcome", "primary", "secondary", "endpoint"],
            "7. Statistical Methods": ["statistical", "analysis", "anova", "t-test"],
            "8. Experimental Animals": ["species", "strain", "age", "weight", "source"],
            "9. Experimental Procedures": ["procedure", "treatment", "dosing", "administration"],
            "10. Results": ["result", "mean", "sd", "sem", "confidence interval"]
        }
        
        for item, keywords in checks.items():
            found = any(kw in text_lower for kw in keywords)
            results["compliance"][item] = found
            if found:
                results["score"] += 1
            else:
                results["recommendations"].append(f"Missing content for {item}")
        
        results["percentage"] = round(results["score"] / results["max_score"] * 100, 1)
        
        return results
    
    def save_protocol(self, content: str, filepath: str):
        """Save protocol to file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Protocol saved to: {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="ARRIVE Guideline Architect - Design animal experiment protocols based on ARRIVE 2.0 standards"
    )
    parser.add_argument("--interactive", "-i", action="store_true", 
                        help="Interactive experiment design wizard")
    parser.add_argument("--input", "-in", type=str,
                        help="Input JSON file path")
    parser.add_argument("--output", "-o", type=str, default="protocol.md",
                        help="Output file path (default: protocol.md)")
    parser.add_argument("--validate", "-v", type=str,
                        help="Validate existing protocol file")
    parser.add_argument("--checklist", "-c", action="store_true",
                        help="Generate ARRIVE 2.0 checklist")
    parser.add_argument("--format", "-f", type=str, default="markdown",
                        choices=["markdown", "text"],
                        help="Output format")
    
    args = parser.parse_args()
    
    architect = ARRIVEGuidelineArchitect()
    
    if args.checklist:
        # Generate checklist
        checklist = architect.generate_checklist(args.format)
        architect.save_protocol(checklist, args.output)
        print("\n📋 ARRIVE 2.0 checklist generated!")
        
    elif args.validate:
        # Validate existing protocol
        try:
            with open(args.validate, 'r', encoding='utf-8') as f:
                protocol_text = f.read()
            
            results = architect.validate_protocol(protocol_text)
            
            print(f"\n{'='*50}")
            print("ARRIVE 2.0 Compliance Validation Report")
            print(f"{'='*50}")
            print(f"\nCompliance score: {results['score']}/{results['max_score']} ({results['percentage']}%)")
            
            print("\nItem-by-item check results:")
            for item, compliant in results['compliance'].items():
                status = "✅" if compliant else "❌"
                print(f"  {status} {item}")
            
            if results['recommendations']:
                print("\nImprovement suggestions:")
                for rec in results['recommendations']:
                    print(f"  • {rec}")
            else:
                print("\n🎉 Congratulations! Your protocol meets all ARRIVE 2.0 essential requirements!")
                
        except FileNotFoundError:
            print(f"❌ Error: File not found {args.validate}")
            sys.exit(1)
            
    elif args.input:
        # Generate protocol from file
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            protocol = architect.generate_protocol(data, args.format)
            architect.save_protocol(protocol, args.output)
            print(f"\n✅ Experiment protocol generated: {args.output}")
            
        except FileNotFoundError:
            print(f"❌ Error: Input file not found {args.input}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ Error: Input file is not valid JSON format")
            sys.exit(1)
            
    elif args.interactive:
        # Interactive wizard
        data = architect.interactive_design()
        protocol = architect.generate_protocol(data, args.format)
        architect.save_protocol(protocol, args.output)
        
        print(f"\n{'='*50}")
        print("✅ Experiment protocol design complete!")
        print(f"{'='*50}")
        print(f"\nFile saved to: {args.output}")
        print(f"Total animals: {data.get('total_animals', 'N/A')}")
        print(f"Number of groups: {len(data.get('groups', []))}")
        print("\nNext steps:")
        print("  1. Submit protocol to institutional ethics committee for approval")
        print("  2. Conduct pilot experiments based on protocol")
        print("  3. Use --validate to verify final protocol completeness")
        
    else:
        # Show help
        parser.print_help()
        print("\n💡 Tip: Use --interactive to launch interactive wizard")


if __name__ == "__main__":
    main()
