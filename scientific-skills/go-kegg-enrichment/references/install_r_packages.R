# R Package Installation Script for GO/KEGG Enrichment
# Run this in R to install all required packages

# CRAN packages
cran_packages <- c("ggplot2", "dplyr", "readr", "jsonlite", "RColorBrewer")

# Install CRAN packages
for (pkg in cran_packages) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    install.packages(pkg)
  }
}

# Bioconductor packages
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

bioc_packages <- c(
  "clusterProfiler",
  "enrichplot",
  "pathview",
  "DOSE",
  "org.Hs.eg.db",   # Human
  "org.Mm.eg.db",   # Mouse
  "org.Rn.eg.db",   # Rat
  "org.Dr.eg.db",   # Zebrafish
  "org.Dm.eg.db",   # Fly
  "org.Sc.sgd.db"   # Yeast
)

for (pkg in bioc_packages) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    BiocManager::install(pkg)
  }
}

cat("Installation complete!\n")
