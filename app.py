import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="Publication-Grade Dual-Axis Plotter", layout="wide"
)

st.title("📊 Publication-Grade Graph Generator (Dual Y-Axis)")
st.markdown(
    "Upload your dataset (CSV or Excel) and customize a publication-ready figure with a linked secondary Y-axis (ideal for catalysis data like conversion/yield vs. productivity)."
)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV or Excel file", type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
  # Read file
  try:
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.sidebar.success("File successfully loaded!")
  except Exception as e:
    st.sidebar.error(f"Error loading file: {e}")
    st.stop()

  st.subheader("📋 Raw Data Preview")
  st.dataframe(df.head())

  numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

  if len(numeric_columns) < 3:
    st.warning(
        "Please ensure your dataset has at least 3 numeric columns (X-axis,"
        " Left Y, Right Y)."
    )
  else:
    st.sidebar.header("2. Axis Mapping")
    x_col = st.sidebar.selectbox(
        "Select X-Axis",
        numeric_columns,
        index=0 if "Stoichiometric number" not in numeric_columns else numeric_columns.index("Stoichiometric number")
    )

    # Left Y-axis selections (Multiple variables allowed)
    left_y_cols = st.sidebar.multiselect(
        "Select Left Y-Axis Variable(s) (e.g., Conversion / Yield)",
        [col for col in numeric_columns if col != x_col],
        default=[numeric_columns[1]]
        if len(numeric_columns) > 1
        else [],
    )

    # Right Y-axis selection (Single variable, e.g., Productivity)
    remaining_cols = [
        col for col in numeric_columns if col != x_col and col not in left_y_cols
    ]
    right_y_col = st.sidebar.selectbox(
        "Select Right Y-Axis Variable (e.g., Productivity)",
        [None] + remaining_cols,
    )

    st.sidebar.header("3. Publication Styling")
    fig_width = st.sidebar.slider("Figure Width (inches)", 4.0, 10.0, 6.0, 0.5)
    fig_height = st.sidebar.slider("Figure Height (inches)", 3.0, 8.0, 5.0, 0.5)
    font_size = st.sidebar.slider("Base Font Size", 8, 16, 12, 1)

    x_label_custom = st.sidebar.text_input(
        "X-Axis Label Customization", value=x_col
    )
    left_label_custom = st.sidebar.text_input(
        "Left Y-Axis Label Customization", value="Conversion / Yield (%)"
    )
    right_label_custom = st.sidebar.text_input(
        "Right Y-Axis Label Customization",
        value=right_y_col
        if right_y_col
        else "MeOH Productivity (g_MeOH kg_cat^-1 h^-1)",
    )

    # --- PLOTTING ENGINE ---
    plt.rcParams.update({
        "font.size": font_size,
        "font.family": "sans-serif",
        "axes.linewidth": 1.2,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
    })

    fig, ax1 = plt.subplots(figsize=(fig_width, fig_height))

    # Plot Left Y variables
    lines = []
    for col in left_y_cols:
      # Check if it's thermo (dashed) or exp (solid) based on name
      linestyle = "--" if any(k in col.lower() for k in ["thermo", "th", "calc"]) else "-"
      marker = "o" if not linestyle == "--" else ""
      (line,) = ax1.plot(
          df[x_col],
          df[col],
          label=col,
          linestyle=linestyle,
          marker=marker,
          linewidth=2,
      )
      lines.append(line)

    ax1.set_xlabel(x_label_custom, fontweight="bold", fontsize=font_size + 1)
    ax1.set_ylabel(
        left_label_custom, fontweight="bold", fontsize=font_size + 1
    )
    ax1.grid(True, linestyle=":", alpha=0.5)

    # Plot Right Y variable if selected
    if right_y_col:
      ax2 = ax1.twinx()
      (line2,) = ax2.plot(
          df[x_col],
          df[right_y_col],
          label=right_y_col,
          color="brown",
          linestyle="-",
          marker="s",
          linewidth=2,
      )
      ax2.set_ylabel(
          right_label_custom,
          color="brown",
          fontweight="bold",
          fontsize=font_size + 1,
      )
      ax2.tick_params(axis="y", labelcolor="brown")
      lines.append(line2)

      # Combine legends from both axes cleanly
      labs = [l.get_label() for l in lines]
      ax1.legend(lines, labs, loc="upper left", frameon=True, facecolor="white", edgecolor="black", framealpha=0.9)
    else:
      ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="black", framealpha=0.9)

    plt.tight_layout()

    # --- RENDER IN STREAMLIT ---
    st.subheader("📈 Generated Publication Figure")
    st.pyplot(fig)

    # --- EXPORT OPTIONS ---
    st.sidebar.header("4. Export Figure")
    dpi_choice = st.sidebar.selectbox("Export Resolution (DPI)", [300, 600, 1200], index=0)
    file_format = st.sidebar.selectbox("File Format", ["png", "pdf", "svg"], index=0)

    import io
    buf = io.BytesIO()
    fig.savefig(buf, format=file_format, dpi=dpi_choice, bbox_inches="tight")
    buf.seek(0)

    st.sidebar.download_button(
        label=f"📥 Download Figure as .{file_format}",
        data=buf,
        file_name=f"publication_figure.{file_format}",
        mime=f"image/{file_format}",
    )

else:
  st.info(
      "👈 Upload a CSV or Excel spreadsheet using the sidebar to start"
      " building your figure."
  )
  
  # Show an example of expected format
  st.markdown("### Example Data Structure Expected:")
  sample_data = pd.DataFrame({
      "Stoichiometric number": [0.4, 0.9, 1.3],
      "XCOx (Exp.)": [3.8, 10.0, 12.4],
      "YMeOH (Thermo.)": [19.0, 35.0, 40.0],
      "Productivity": [351.05, 552.6, 608.18]
  })
  st.dataframe(sample_data)
