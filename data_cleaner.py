# This code is used for cleaning common words and other biased words from the word_freq.json file created by analyzer
import json

dir = "word_freq.json"
with open(dir, "r") as f:
    word_freq = json.load(f)

# Exclude common words
dir = "1000_common_words.json"
with open(dir, "r") as f:
    common_words = json.load(f)



# More common words
extended_common_words = ["also", "time", "score", "view", "animal", "reason", "upper"
                         , "plus", "yellow", "adult", "purple", "row", "closed", "video",
                         "rabbit", "thousand", "international", "mirror", "wall", "online",
                         "plan", "southern", "go", "bootstrap", "northern"]

# Specific field-related words. Like medical terms.
biased_words = ["phenotype", "substrate", "serum", "amino", "temporal",
                               "lysis", "enzyme", "protease", "peptide", "nucleotide",
                               "bioscience", "canonical", "chromatography", "spectre"
                               , "allele", "genotype", "python", "glycerol", "antigen",
                               "polymarase", "chromatin", 'immunofluorescence', "ligation",
                               "mycoplasma", "ligand", "transduce", "antigen", "methanol",
                               "atlas", "lipid", "spectroscopy", "mutagenesis", "monoclonal",
                               "epithelial", "embryonic", "hallmark", "chimera", "kinase",
                               "perfusion", "dendrite", "phenotypic", "cortical", "formic",
                               "synaptic", "enzymatic", "trypsin", "fibroblast"]

keys = list(word_freq.keys())
for key in keys:
    if key in common_words + extended_common_words + biased_words:
        del word_freq[key]

output_file = "word_freq(cleaned).json"
with open(output_file, 'w') as f:
    json.dump(word_freq, f, indent = 4)
