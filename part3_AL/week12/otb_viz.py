# %% Setup - Imports
import json
import os

import pandas as pd
from plotnine import *
from sqlalchemy import create_engine

from config import DSN

# %% Setup - Load data
engine = create_engine(DSN)

fossils = pd.read_sql(
    """
    SELECT f.*, t.scientific_name, l.*
    FROM fossils f
    JOIN taxa t USING (taxon_id)
    JOIN localities l USING (locality_id)
    """,
    engine,
)

# set the path to the week 11 folder so the file can be located
path = os.path.join("part3_AL/week11/ecv_by_specimen.csv")
ecv_full = pd.read_csv(path)

# Make grade a categorical variable
grade_order = ["archaic", "mega", "trans", "pre.mod"]
ecv_full["grade"] = pd.Categorical(
    ecv_full["grade"], categories=grade_order, ordered=True
)

# %% Setup - Create taxon_map
taxon_map = {
    "Australopithecus Dart, 1925": "Australopithecus",
    "Australopithecus anamensis Leakey et al., 1995": "Au. anamensis",
    "Hominini": "Hominini",
    "Homo Linnaeus, 1758": "Homo",
    "Homo erectus (Dubois, 1892)": "H. erectus",
    "Homo habilis Leakey, Tobias & Napier, 1964": "H. habilis",
    "Kenyanthropus platyops Leakey et al., 2001": "K. platyops",
    "Paranthropus Broom, 1938": "Paranthropus",
    "Paranthropus aethiopicus (Arambourg & Coppens, 1967)": "P. aethiopicus",
    "Paranthropus boisei (Leakey, 1959)": "P. boisei",
}

# Create a taxon_name row in the fossils.df
fossils["taxon_name"] = fossils["scientific_name"].map(taxon_map)
print(fossils["taxon_name"])
print(fossils["taxon_name"].isnull().sum())

# %% Setup - Create fossils_ecv
ecv_by_taxon = (
    ecv_full.groupby("taxon")["ecv_median_cm3"]
    .agg(
        ecv_mean="mean",
        ecv_median="median",
        ecv_min="min",
        ecv_max="max",
        ecv_n="count",
    )
    .reset_index()
)
print(ecv_by_taxon)

fossils_ecv = pd.merge(
    fossils, ecv_by_taxon, left_on="taxon_name", right_on="taxon", how="left"
)
print(
    fossils_ecv.shape
)  # rows should equal fossils.shape (left join preserves all rows)
print(fossils_ecv["ecv_mean"].isnull().sum())  # taxa with no ECV data

# %% [markdown]
# Part 1 - Univariate Distrubtions

# %% 1.1 Histogram
# The different binwidths I chose were 50 (used in the example), 10, and 100
# OG=50
histogram1 = (
    ggplot(ecv_full, aes(x="ecv_median_cm3"))
    + geom_histogram(binwidth=50, fill="steelblue", color="white")
    + labs(
        x="Endocranial volume (cm³)",
        y="Count",
        title="Distribution of hominin ECV estimates",
    )
    + theme_bw()
)
histogram1.save("ecv_histogram1.png", dpi=150)

# binwidth = 10
histogram2 = (
    ggplot(ecv_full, aes(x="ecv_median_cm3"))
    + geom_histogram(binwidth=10, fill="steelblue", color="white")
    + labs(
        x="Endocranial volume (cm³)",
        y="Count",
        title="Distribution of hominin ECV estimates",
    )
    + theme_grey()
)
histogram2.save("ecv_histogram2.png", dpi=150)

# binwidth = 100
histogram3 = (
    ggplot(ecv_full, aes(x="ecv_median_cm3"))
    + geom_histogram(binwidth=100, fill="steelblue", color="white")
    + labs(
        x="Endocranial volume (cm³)",
        y="Count",
        title="Distribution of hominin ECV estimates",
    )
    + theme_seaborn()
)

histogram3.save("ecv_histogram3.png", dpi=150)

# All together now
for bw, fname in [
    (50, "ecv_histogram1.png"),
    (10, "ecv_histogram2.png"),
    (100, "ecv_histogram3.png"),
]:
    all_histograms = (
        ggplot(ecv_full, aes(x="ecv_median_cm3"))
        + geom_histogram(binwidth=bw, fill="steelblue", color="white")
        + labs(
            x="Endocranial volume (cm³)",
            y="Count",
            title=f"Distribution of hominin ECV estimates (bin = {bw} cm³)",
        )
        + theme_bw()
    )
all_histograms.save(all_histograms, dpi=150)


# %% 1.2 Density Plot
density_plot = (
    ggplot(ecv_full, aes(x="ecv_median_cm3", fill="grade"))
    + geom_density(alpha=0.4)
    + scale_fill_brewer(type="qual", palette="Set2")
    + labs(x="Endocranial volume (cm³)", fill="Grade")
    + theme_bw()
)
density_plot.save("ecv_density_by_grade.png", dpi=150)

# %% [markdown]
# 1.3 Deliverables - Part 1
#
# **1.** How does bin widths change what the plot communitcates
#    - At 50 (histogram1): shows the graph structure the best
#    - At 10 (histogram2): appears to be little specimens counted
#    - At 100 (historgram3): too compact, hard to see true graph structure
#
#   Bin width seems to be an analytical choice and is tricky to get right. It can be too noisy and compact or too separated.
#
# **2.** **(a)** Which grade has the widest ECV range and what might explain this biologically
#    - The pre.mod grade has the widest ECV range: ~500-1300. Biologically, there are two taxa who contribute to this range;
#      H. erectus and H. heidelbergensis.
#
#    **(b)** Where do the trans (H. habilis) and pre.mod distributions overlap, and what does that overlap imply for taxonomic boundaries based on ECV alone?
#    - trans (*H. habilis*) runs 500–780 cm³ and pre.mod starts at 500 cm³, so the two overlap across roughly 550–790 cm³. A specimen in that range
#      cannot be assigned to a grade on ECV alone. ECV is continuous across this boundary.

# %% [markdown]
# Part 2 - Bivariate Relationships

# %% 2.1 Scatter plot
scatter_plot1 = (
    ggplot(
        ecv_full,
        aes(x="age_mid_Ma", y="ecv_median_cm3", color="grade", size="n_estimates"),
    )
    + geom_point(alpha=0.7)
    + scale_x_reverse()  # older ages on the left
    + scale_color_brewer(type="qual", palette="Set1")
    + labs(
        x="Age (Ma)",
        y="ECV (cm³)",
        color="Grade",
        size="N estimates",
        title="Hominin ECV through time",
    )
    + theme_bw()
)
scatter_plot1.save("ecv_vs_age1.png", dpi=150)

# %%
# Point shape varies by grade
scatter_plot2 = (
    ggplot(
        ecv_full,
        aes(
            x="age_mid_Ma",
            y="ecv_median_cm3",
            shape="grade",
            color="grade",
            size="n_estimates",
        ),
    )
    + geom_point(alpha=0.7)
    + scale_x_reverse()  # older ages on the left
    + scale_color_brewer(type="qual", palette="Set1")
    + labs(
        x="Age (Ma)",
        y="ECV (cm³)",
        color="Grade",
        size="N estimates",
        title="Hominin ECV through time",
    )
    + theme_bw()
)
scatter_plot2.save("ecv_vs_age2.png", dpi=150)

# %% 2.2 Adding a trend line
trend_line1 = (
    ggplot(ecv_full, aes(x="age_mid_Ma", y="ecv_median_cm3"))
    + geom_point(aes(color="grade"), alpha=0.6)
    + geom_smooth(method="lm", color="red", linetype="dashed")
    + scale_x_reverse()
    + labs(x="Age (Ma)", y="ECV (cm³)")
    + theme_bw()
)
trend_line1.save("ecv_trend1.png", dpi=150)

# Lines per grade
trend_line2 = (
    ggplot(ecv_full, aes(x="age_mid_Ma", y="ecv_median_cm3", color="grade"))
    + geom_point(alpha=0.6)
    + geom_smooth(method="lm", linetype="dashed", se=False)
    + scale_x_reverse()
    + scale_color_brewer(type="qual", palette="Set1")
    + labs(x="Age (Ma)", y="ECV (cm³)", color="Grade")
    + theme_bw()
)
trend_line2.save("ecv_trend2.png", dpi=200)

# %% 2.3 Boxplot by taxon
# Order taxa by median ECV
taxon_order = (
    ecv_full.groupby("taxon")["ecv_median_cm3"].median().sort_values().index.tolist()
)

ecv_full["taxon"] = pd.Categorical(
    ecv_full["taxon"], categories=taxon_order, ordered=True
)

boxplot = (
    ggplot(ecv_full, aes(x="taxon", y="ecv_median_cm3", fill="grade"))
    + geom_boxplot()
    + coord_flip()  # horizontal boxes, easier to read long labels
    + labs(x="", y="ECV (cm³)", fill="Grade")
    + theme_bw()
    + theme(legend_position="bottom")
)
boxplot.save("ecv_boxplot_taxon.png", dpi=150)

# %% [markdown]
# 2.4 Deliverables - Part 2
#
# **1.** Explaining why encoding the same variable redundantly in both color and shape improves accessibility.
#    - Individuals who are color blind can see or recognize the shapes better than the chosen colors for
#      the graphs. Shapes are also improve accessibility because if a figure is printed in black and white/grey scale you can still
#      tell the grades apart.
#
#
# **2.** Compare the within-grade slopes to the overall slope — does the overall trend accurately describe each grade, or is it misleading?
#    - The overall trend is misleading. pre.mod is the only grade that matches between the two. archaic and mega grades appear to flatten out.
#
#
# **3.** (a) Identify the taxon with the greatest within-taxon ECV variance and a possible explanation
#    - H. erectus has the greatest within-taxon ECV variation. This could be do long temporal span of the species which would cover the
#      brain enlargement within the species or sexual dimorphism.
#
#
#    (b) Identify any taxa whose boxes overlap substantially, and what that implies for using ECV as a taxonomic discriminator.
#    - Au. afarensis, Au. sediba, Au. garhi, Au. africanus, P. aethiopicus, P. boisei, P. robustus, and H. habilis taxa overlap substantially.
#      While it can be distinctive, ECV is not the best taxonomic discriminator it cannot separate australopiths from parathropines and vice versa.
#      The overlap between the taxa could be misleading. Also, if H. floresiensis (ECV = ~400) was included in this dataset it would
#      overlap with archaic and mega taxa as well.

# %% [markdown]
# Part 3 - OTB Data

# %% 3.1 Specimen counts by taxon and locality
counts = (
    fossils_ecv.groupby(["taxon_name", "subregion"])
    .size()
    .reset_index(name="n_specimens")
)

# Stacked bars
stacked_bars_plot = (
    ggplot(counts, aes(x="subregion", y="n_specimens", fill="taxon_name"))
    + geom_col()  # stacked bar (geom_col uses a pre-computed y)
    + coord_flip()
    + labs(x="", y="Specimens", fill="Taxon")
    + theme_bw()
    + theme(legend_position="bottom", figure_size=(8, 5))
)
stacked_bars_plot.save("otb_counts.png", dpi=150)

# Dodged bars
dodged_bars_plot = (
    ggplot(counts, aes(x="subregion", y="n_specimens", fill="taxon_name"))
    + geom_col(position="dodge")
    + coord_flip()
    + labs(x="", y="Specimens", fill="Taxon")
    + theme_bw()
    + theme(legend_position="bottom", figure_size=(8, 5))
)
dodged_bars_plot.save("otb_counts.png", dpi=150)

# %% 3.2 Faceting
# Find taxa with 2 or more specimens
taxon_counts = ecv_full["taxon"].value_counts()
multi_specimen_taxa = taxon_counts[taxon_counts > 1].index

facet = (
    ggplot(
        ecv_full[~ecv_full["taxon"].isin(["Au. sediba", "Au. garhi"])],
        aes(x="age_mid_Ma", y="ecv_median_cm3", color="taxon"),
    )
    + geom_point(alpha=0.6)
    + geom_smooth(method="lm", se=False, linetype="dashed", size=0.8)
    + facet_wrap("~taxon", scales="free_y")
    + scale_x_reverse()
    + labs(x="Age (Ma)", y="Median ECV (cm³)")
    + theme_bw()
    + theme(
        legend_position="none",  # redundant with facet labels
        figure_size=(10, 6),
    )
)
facet.save("otb_ecv_faceted.png", dpi=150)

# %% Heatmap
# Create locality counts like taxon counts
locality_counts = (
    fossils_ecv.groupby(["taxon_name", "locality"])
    .size()
    .reset_index(name="n_specimens")
)

# locality_counts = (fossils_ecv
# .groupby(['taxon_name', 'subregion']) #with subregions because locality is hard to read
# .size()
# .reset_index(name='n_specimens')
# )

small_locality_counts = (
    fossils_ecv["locality"].value_counts().head(10).index
)  # index the 10 taxa with the most specimens; 'locality' produced too many names.
heatmap_df = locality_counts[
    locality_counts["locality"].isin(small_locality_counts)
]  # create a small dataframe for the smaller locality counts

heatmap = (
    ggplot(heatmap_df, aes(x="taxon_name", y="locality", fill="n_specimens"))
    + geom_tile(color="white")
    + scale_fill_gradient(low="#f7fbff", high="#08306b")
    + coord_equal()
    + labs(x="", y="", fill="Specimens", title="OTB Fossils Heatmap")
    + theme(
        axis_text_x=element_text(
            rotation=45, ha="right"
        ),  # slant the taxon_names so they are easy to read
        axis_text_y=element_text(
            margin={"r": 6, "units": "pt"}
        ),  # fit locality name to give room/space for the full name
        figure_size=(8, 6),
    )
)
heatmap.save("otb_heatmap.png", dpi=150)

# %% [markdown]
# 3.3 Deliverables - Part 3
#
# 1. Explain when you would prefer stacked vs. dodged bars
#    - I would prefer dodged bars over stacked bars because it is easier to read when comparing counts by taxa across each locality. It is also easier
#      to see the counts for individual taxa, in the stacked bars few I really couldn't tell the amount for each taxon.
#
# 2. Describe the within-taxon trend for at least two taxa: does ECV change with age
#    within that taxon in your OTB sample?
#
#    - ***H. erectus*** (~1.9–0.34 Ma): a clear increase in ECV through time. Early specimens (~600) are at the bottom of the range, and later specimens exceed 1000.
#   This is the one taxon with a strong within-taxon trend.
#
#    - ***P. boisei*** (~2.2–1.42 Ma): nearly flat, consistent with stasis in brain size.
#
# 3. Reading the heatmap: which locality–taxon combinations are most represented, and
#    which are absent? What does the absence pattern suggest about sampling bias or paleoecology?
#    - I only used 10 localities so the heatmap was easy to see.
#       - Most represented:
#         - Kanapoin - Au. anamensis
#         - Nachukui, Locality NK-3 - H.erectus
#
#       - Absent
#         - K. platyops only appears at Nuchukui, Locality LO-5
#         - Paranthropus and P. boisei are only found in Koobi Fora and Ileret
#
#   Sampling bias: Kanapoi's count reflects one taxon. Counts are primarily specimens, not individuals, so
#   localities rich in isolated teeth could look inflated. The genus-level rows (Hominini, *Homo*, *Paranthropus*) are fragmentary material that could
#   not be identified to species.

# %% [markdown]
# Part 4 - Figure Quality

# %% Figure Improvements
# Part 4 - Improved scatter plot from section 2.1 (ECV vs. age by grade)
improve_1470 = ecv_full[ecv_full["ID"] == "KNM-ER 1470"]

# Point and label positions for KNM-ER 1470
x0 = improve_1470["age_mid_Ma"].iloc[0]
y0 = improve_1470["ecv_median_cm3"].iloc[0]
lab_x, lab_y = (
    x0 + 0.25,
    y0 + 150,
)  # move the label up and to the left from standard position

pub_fig = (
    ggplot(
        ecv_full, aes(x="age_mid_Ma", y="ecv_median_cm3", color="grade", shape="grade")
    )
    + geom_point(size=3, alpha=0.8)
    + annotate(
        "segment", x=lab_x, y=lab_y - 20, xend=x0, yend=y0, color="black", size=0.4
    )
    + annotate("text", x=lab_x, y=lab_y, label="KNM-ER 1470", size=9, color="black")
    + scale_x_reverse(labels=lambda xs: [f"{x:.1f} Ma" for x in xs])
    + scale_color_manual(
        values=["#1b9e77", "#d95f02", "#7570b3", "#e7298a"]
    )  # colorblind friendly colors; actually address the problem Denné asked for
    # + scale_color_manual(values=['#86d43a', '#51bbe7', '#df414d', '#f7902E']) #powerpuff girl colors; for cuteness
    + labs(
        x="Geological age",
        y="Endocranial volume (cm³)",
        color="Grade",
        shape="Grade",
        title="Hominin endocranial volume through time",
        caption="Source: Du et al. 2026",
    )
    + theme_bw()
    + theme(
        axis_text=element_text(size=11),
        axis_title=element_text(size=12),
        plot_title=element_text(size=13),
        legend_position="right",
    )
)
pub_fig.save("pub_figure.png", dpi=300, width=7, height=5)

# %% [markdown]
# Deliverables - Part 4
# Explain each choice: what problem did each change solve, and who is the intended audience for this figure?
#
# 1. **Custom palette (`scale_color_manual`)** — olors chosen to stay distinguishable for common color-vision deficiencies
#      and in print and for colorblind readers.
#
# 2. **Redundant shape encoding** — grade is shown by both color and shape, figure still works in grayscale.
#
# 3. **Tick formatting ("1.5 Ma")** — puts the units on the axis itself, so the reader immediately sees these are ages in millions of years,
#     not a standard numbers.
#
# 4. **Annotation (`geom_text`)** — labels KNM-ER 1470, it points the reader to the specimen the text discusses
#    and that matters most for the species-delimitation argument.
#
# 5. **Caption** — credits the data source in the figure
#
# 6. **Font sizes** — the default text is small at 7 × 5 in; 11–13 pt
#    keeps labels legible when the figure is scaled to a page column.
#
# 7. **300 dpi at 7 × 5 in** — print resolution at a size that fits a
#    standard page width. 150 dpi looks fuzzy printed.