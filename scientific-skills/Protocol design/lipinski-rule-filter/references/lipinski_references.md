# Lipinski Rule of Five - References

## Original Publication

**Lipinski, C. A., Lombardo, F., Dominy, B. W., & Feeney, P. J. (1997).**
Experimental and computational approaches to estimate solubility and permeability in drug discovery and development settings.
*Advanced Drug Delivery Reviews, 23*(1-3), 3-25.
DOI: 10.1016/S0169-409X(96)00423-1

## Key Concepts

### Lipinski's Rule of Five
A compound is likely to have poor absorption or permeability if it violates more than one of the following rules:
1. Molecular weight > 500 Da
2. LogP > 5
3. H-bond donors > 5
4. H-bond acceptors > 10

### Implementation Notes
- This tool uses RDKit for molecular property calculation
- Default threshold allows ≤ 1 violation ("Rule of 5 compliant")
- Violations are calculated based on exact thresholds (≥ 500, not > 500)

## Related Work

- Veber, D. F., et al. (2002). Molecular properties that influence the oral bioavailability of drug candidates. *J. Med. Chem.*, 45(12), 2615-2623.
- Ghose, A. K., et al. (1999). A knowledge-based approach in designing combinatorial or medicinal chemistry libraries for drug discovery. *J. Comb. Chem.*, 1(1), 55-68.

## Software

- RDKit: Open-source cheminformatics toolkit
  - Website: https://www.rdkit.org/
  - Documentation: https://rdkit.readthedocs.io/
