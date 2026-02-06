# References and Resources for Survival Analysis

## Original Papers

### 1. Kaplan-Meier Estimator
**Kaplan EL, Meier P (1958)**. "Nonparametric estimation from incomplete observations." 
*Journal of the American Statistical Association*, 53(282):457-481.
- Original description of the product-limit estimator
- Foundation of modern survival analysis

### 2. Cox Proportional Hazards Model
**Cox DR (1972)**. "Regression models and life-tables."
*Journal of the Royal Statistical Society: Series B*, 34(2):187-220.
- Seminal paper on proportional hazards regression
- Most cited paper in statistics

### 3. Log-Rank Test
**Peto R, Peto J (1972)**. "Asymptotically efficient rank invariant test procedures."
*Journal of the Royal Statistical Society: Series A*, 135(2):185-207.
- Description of the log-rank test (also called Mantel-Cox test)

## Books

### 1. Klein & Moeschberger
**Klein JP, Moeschberger ML (2003)**. "Survival Analysis: Techniques for Censored and Truncated Data." 2nd ed.
*Springer*
- Comprehensive graduate-level textbook
- Covers theory and applications

### 2. Therneau & Grambsch
**Therneau TM, Grambsch PM (2000)**. "Modeling Survival Data: Extending the Cox Model."
*Springer*
- Advanced topics in Cox regression
- Time-dependent covariates, frailty models

### 3. Collett
**Collett D (2015)**. "Modelling Survival Data in Medical Research." 3rd ed.
*CRC Press*
- Medical/clinical focus
- Practical examples with SAS, R

## Reporting Guidelines

### ATN Requirements
For clinical trials reporting:
- CONSORT statement for randomized trials
- Follow ATN (Aide au Tacrolimus Nomogram) guidelines for immunosuppression studies

### Key Elements to Report
1. Sample size and censoring rate
2. Median survival with 95% confidence intervals
3. Number at risk at regular intervals
4. Log-rank test statistic and p-value
5. Hazard ratios with 95% CI
6. Test for proportional hazards assumption

## Software Resources

### Python
- **lifelines**: https://lifelines.readthedocs.io/
  - Most comprehensive Python survival analysis library
  - Includes Kaplan-Meier, Cox model, AFT models
  
- **scikit-survival**: https://scikit-survival.readthedocs.io/
  - Scikit-learn compatible survival models
  - Random survival forests, gradient boosting

### R
- **survival**: Core survival analysis package (Therneau)
- **survminer**: Publication-ready plots
- **survcomp**: Performance assessment

## Common Pitfalls

### 1. Proportional Hazards Violation
- Check using Schoenfeld residuals
- Solution: Time-dependent coefficients, stratification

### 2. Informative Censoring
- Standard methods assume censoring is non-informative
- Consider sensitivity analyses

### 3. Small Sample Sizes
- < 50 events: Results may be unstable
- Consider exact methods or Bayesian approaches

### 4. Competing Risks
- Standard KM may overestimate risk
- Use cumulative incidence functions for competing risks

## Sample Datasets

See `sample_data.csv` for example format:
- Patient ID
- Survival time (months)
- Event indicator (1=death, 0=censored)
- Treatment group
- Additional covariates (age, sex, etc.)
