import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="Publication-Grade Dual-Axis Plotter", layout="wide"
)

st.title("📊 Publication-Grade Graph Generator (Dual Y-Axis)")
st.markdown(
    "Upload your dataset, customize Origin-style 3D spheres, font colors, axis limits, and export high-res figures."
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
    default_x_idx = (
        numeric_columns.index("Stoichiometric number")
        if "Stoichiometric number" in numeric_columns
        else 0
    )
    x_col = st.sidebar.selectbox(
        "Select X-Axis", numeric_columns, index=default_x_idx
    )

    # Left Y-axis selections (Multiple variables allowed)
    left_y_cols = st.sidebar.multiselect(
        "Select Left Y-Axis Variable(s)",
        [col for col in numeric_columns if col != x_col],
        default=[numeric_columns[1]]
        if len(numeric_columns) > 1
        else [],
    )

    # Right Y-axis selection (Single variable)
    remaining_cols = [
        col for col in numeric_columns if col != x_col and col not in left_y_cols
    ]
    right_y_col = st.sidebar.selectbox(
        "Select Right Y-Axis Variable (e.g., Productivity)",
        [None] + remaining_cols,
    )

    st.sidebar.header("3. Line Colors & Styles")
    
    # Dynamic color pickers for each selected line
    line_colors = {}
    default_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    
    color_idx = 0
    for col in left_y_cols:
      default_c = default_colors[color_idx % len(default_colors)]
      line_colors[col] = st.sidebar.color_picker(f"Color for: {col}", default_c)
      color_idx += 1

    if right_y_col:
      line_colors[right_y_col] = st.sidebar.color_picker(
          f"Color for Right Y: {right_y_col}", "#8c564b"
      )

    # Marker Styling (Origin-style 3D Glossy Sphere Effect)
    st.sidebar.header("4. Marker, Font & Color Styling")
    use_3d_spheres = st.sidebar.checkbox(
        "Use Origin-Style 3D Glossy Sphere Markers", value=True
    )
    
    font_family_choice = st.sidebar.selectbox(
        "Font Family", ["sans-serif", "serif", "monospace", "DejaVu Sans"], index=0
    )

    # Font Color Controls
    st.markdown("### 🎨 Font Colors")
    tick_color = st.sidebar.color_picker("Axis Ticks & Numbers Color", "#000000")
    x_title_color = st.sidebar.color_picker("X-Axis Title Color", "#000000")
    left_title_color = st.sidebar.color_picker("Left Y-Axis Title Color", "#000000")
    right_title_color = st.sidebar.color_picker("Right Y-Axis Title Color", "#8c564b") if right_y_col else "#000000"

    st.sidebar.header("5. Axis Limits & Layout")
    
    # Auto or Custom X-Limits
    auto_x = st.sidebar.checkbox("Auto X-Axis Limits", value=True)
    if not auto_x:
      x_min = st.sidebar.number_input("X Min", value=float(df[x_col].min()))
      x_max = st.sidebar.number_input("X Max", value=float(df[x_col].max()))

    # Auto or Custom Left Y-Limits
    auto_y1 = st.sidebar.checkbox("Auto Left Y-Axis Limits", value=True)
    if not auto_y1:
      y1_min = st.sidebar.number_input("Left Y Min", value=0.0)
      y1_max = st.sidebar.number_input("Left Y Max", value=50.0)

    # Auto or Custom Right Y-Limits (if right Y exists)
    if right_y_col:
      auto_y2 = st.sidebar.checkbox("Auto Right Y-Axis Limits", value=True)
      if not auto_y2:
        y2_min = st.sidebar.number_input("Right Y Min", value=0.0)
        y2_max = st.sidebar.number_input("Right Y Max", value=800.0)

    # Legend Position Control
    legend_loc = st.sidebar.selectbox(
        "Legend Position",
        [
            "upper left",
            "upper right",
            "lower left",
            "lower right",
            "center left",
            "center right",
            "best",
        ],
        index=0,
    )

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
        value=right_y_col if right_y_col else "Productivity",
    )

    # --- PLOTTING ENGINE ---
    plt.rcParams.update({
        "font.size": font_size,
        "font.family": font_family_choice,
        "axes.linewidth": 1.2,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
    })

    fig, ax1 = plt.subplots(figsize=(fig_width, fig_height))

    # Helper function to draw Origin-style 3D glossy spheres
    def plot_origin_3d_spheres(ax, x, y, color):
      # 1. Subtle drop shadow layer behind the sphere for depth
      ax.scatter(x, y, s=110, color="black", alpha=0.15, zorder=3, linewidths=0)
      # 2. Main colored sphere body
      ax.scatter(x, y, s=80, color=color, edgecolor="#222222", linewidth=1.0, zorder=4)
      # 3. Specular highlight (glossy reflection dot offset to top-left)
      # Approximate data-to-pixel offset for highlight reflection
      x_data = np.array(x)
      y_data = np.array(y)
      ax.scatter(x_data, y_data, s=15, color="white", alpha=0.75, zorder=5, linewidths=0)

    # Plot Left Y variables
    lines = []
    for col in left_y_cols:
      linestyle = (
          "--"
          if any(k in col.lower() for k in ["thermo", "th", "calc"])
          else "-"
      )
      
      has_markers = (linestyle == "-")
      
      # Plot connector line first
      (line,) = ax1.plot(
          df[x_col],
          df[col],
          label=col,
          color=line_colors[col],
          linestyle=linestyle,
          marker="" if use_3d_spheres and has_markers else ("o" if has_markers else ""),
          markersize=6,
          markerfacecolor=line_colors[col],
          markeredgecolor="black",
          linewidth=2,
          zorder=2,
      )
      
      # Overlay Origin-style 3D spheres if enabled and it's a dotted/solid data line with markers
      if use_3d_spheres and has_markers:
        plot_origin_3d_spheres(ax1, df[x_col], df[col], line_colors[col])

      lines.append(line)

    # Style X and Left Y axes
    ax1.set_xlabel(x_label_custom, fontweight="bold", fontsize=font_size + 1, color=x_title_color)
    ax1.set_ylabel(left_label_custom, fontweight="bold", fontsize=font_size + 1, color=left_title_color)
    ax1.tick_params(axis="x", colors=tick_color)
    ax1.tick_params(axis="y", colors=tick_color, labelcolor=tick_color)
    ax1.grid(True, linestyle=":", alpha=0.5)

    # Apply X limits if custom
    if not auto_x:
      ax1.set_xlim(x_min, x_max)

    # Apply Left Y limits if custom
    if not auto_y1:
      ax1.set_ylim(y1_min, y1_max)

    # Plot Right Y variable if selected
    if right_y_col:
      ax2 = ax1.twinx()
      
      (line2,) = ax2.plot(
          df[x_col],
          df[right_y_col],
          label=right_y_col,
          color=line_colors[right_y_col],
          linestyle="-",
          marker="" if use_3d_spheres else "o",
          markersize=6,
          linewidth=2,
          zorder=2,
      )
      
      if use_3d_spheres:
        plot_origin_3d_spheres(ax2, df[x_col], df[right_y_col], line_colors[right_y_col])

      ax2.set_ylabel(
          right_label_custom,
          color=right_title_color,
          fontweight="bold",
          fontsize=font_size + 1,
      )
      ax2.tick_params(axis="y", colors=tick_color, labelcolor=tick_color)
      
      # Apply Right Y limits if custom
      if not auto_y2:
        ax2.set_ylim(y2_min, y2_max)

      lines.append(line2)

      # Combine legends from both axes and place according to user selection
      labs = [l.get_label() for l in lines]
      ax1.legend(
          lines,
          labs,
          loc=legend_loc,
          frameon=True,
          facecolor="white",
          edgecolor="black",
          framealpha=0.9,
      )
    else:
      ax1.legend(
          loc=legend_loc,
          frameon=True,
          facecolor="white",
          edgecolor="black",
          framealpha=0.9,
      )

    plt.tight_layout()

    # --- RENDER IN STREAMLIT ---
    st.subheader("📈 Generated Publication Figure")
    st.pyplot(fig)

    # --- EXPORT OPTIONS ---
    st.sidebar.header("6. Export Figure")
    dpi_choice = st.sidebar.selectbox(
        "Export Resolution (DPI)", [300, 600, 1200], index=0
    )
    file_format = st.sidebar.selectbox("File Format", ["png", "pdf", "svg"], index=0)

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
