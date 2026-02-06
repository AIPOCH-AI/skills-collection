# Example Citations for Testing

## Input Examples (Various Formats)

### APA Format
1. Smith, J. A., Jones, M. B., & Brown, K. L. (2020). Effects of treatment on patient outcomes in clinical trials. Journal of the American Medical Association, 324(15), 1523-1531. https://doi.org/10.1001/jama.2020.12345

2. Zhang, L., Chen, Y., Wang, H., Li, X., Liu, M., Chen, S., & Wu, J. (2021). Novel approaches to cancer immunotherapy. Nature Medicine, 27(3), 412-425.

### MLA Format
1. Smith, John A., et al. "Effects of Treatment on Patient Outcomes." JAMA, vol. 324, no. 15, 2020, pp. 1523-31.

2. Zhang, Li, et al. "Novel Approaches to Cancer Immunotherapy." Nature Medicine, vol. 27, no. 3, 2021, pp. 412-25.

### Vancouver Format
1. Smith JA, Jones MB, Brown KL. Effects of treatment on patient outcomes in clinical trials. JAMA. 2020;324(15):1523-1531.

2. Zhang L, Chen Y, Wang H, Li X, Liu M, Chen S, et al. Novel approaches to cancer immunotherapy. Nat Med. 2021;27(3):412-425.

### BibTeX Format
```bibtex
@article{smith2020effects,
  author = {Smith, John A. and Jones, Michael B. and Brown, Karen L.},
  title = {Effects of treatment on patient outcomes in clinical trials},
  journal = {Journal of the American Medical Association},
  year = {2020},
  volume = {324},
  number = {15},
  pages = {1523--1531},
  doi = {10.1001/jama.2020.12345}
}
```

### Free Text / Unstructured
1. Smith JA, Jones MB, Brown KL. Effects of treatment on patient outcomes. Journal of the American Medical Association 2020, 324(15):1523-1531

2. Zhang L et al wrote about Novel approaches to cancer immunotherapy in Nature Medicine 2021, volume 27 issue 3 pages 412-425

## Expected AMA Output

```
Smith JA, Jones MB, Brown KL. Effects of treatment on patient outcomes in clinical trials. JAMA. 2020;324(15):1523-1531. doi:10.1001/jama.2020.12345

Zhang L et al. Novel approaches to cancer immunotherapy. Nat Med. 2021;27(3):412-425.
```
