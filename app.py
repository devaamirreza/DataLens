import io
import hashlib

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from datalens.profiling import (
    profile_dataset,
    inspect_data_types,
)
from datalens.pipeline import clean_dataset


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="DataLens | Data Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# 2. APPLICATION STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 36px;
            font-weight: 700;
        }

        .subtitle {
            font-size: 16px;
            color: #808495;
        }

        div[data-testid="stMetric"] {
            background-color: #f8f9fc;
            padding: 18px;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
        }

        div[data-testid="stStatusWidget"] {
            border-radius: 10px;
        }

        /* Export buttons turn green only when their files are ready. */
        .st-key-csv_download_ready div[data-testid="stDownloadButton"] button,
        .st-key-excel_download_ready div[data-testid="stDownloadButton"] button {
            background-color: #15803d !important;
            border: 1px solid #15803d !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        .st-key-csv_download_ready div[data-testid="stDownloadButton"] button:hover,
        .st-key-excel_download_ready div[data-testid="stDownloadButton"] button:hover {
            background-color: #166534 !important;
            border-color: #166534 !important;
            color: #ffffff !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 3. REUSABLE DATA QUALITY CHART
# --------------------------------------------------

def create_quality_chart(
    good_value: float,
    issue_value: float,
    good_label: str,
    issue_label: str,
) -> go.Figure:
    """
    Create a stacked horizontal bar chart.

    Green represents the healthy portion.
    Red represents the portion requiring attention.
    """

    fig = go.Figure()

    # Healthy portion.
    fig.add_trace(
        go.Bar(
            x=[good_value],
            y=["Quality"],
            name=good_label,
            orientation="h",
            marker_color="#16A34A",
            hovertemplate=(
                f"{good_label}: %{{x:.2f}}%"
                "<extra></extra>"
            ),
        )
    )

    # Issue portion.
    fig.add_trace(
        go.Bar(
            x=[issue_value],
            y=["Quality"],
            name=issue_label,
            orientation="h",
            marker_color="#DC2626",
            hovertemplate=(
                f"{issue_label}: %{{x:.2f}}%"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        barmode="stack",
        height=85,
        showlegend=False,
        bargap=0.5,
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            title=None,
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
        ),
        margin=dict(
            l=0,
            r=0,
            t=5,
            b=5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# --------------------------------------------------
# 4. DATASET READER
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def load_and_analyze_dataset(file_bytes: bytes, filename: str):
    """
    Load and analyse a dataset once per unique uploaded file.

    Streamlit reruns the script when widgets change. Caching this operation
    prevents CSV/Excel parsing and full-dataset profiling from repeating on
    every interaction (including navigation and cleaning configuration).
    """
    file_buffer = io.BytesIO(file_bytes)

    if filename.lower().endswith(".csv"):
        df = pd.read_csv(file_buffer)
    else:
        df = pd.read_excel(file_buffer, engine="openpyxl")

    profile = profile_dataset(df)
    type_info = inspect_data_types(df)

    return df, profile, type_info


# --------------------------------------------------
# 5. APPLICATION HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🔍 DataLens</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Your intelligent data profiling and cleaning workspace"
    "</div>",
    unsafe_allow_html=True,
)

st.divider()


# --------------------------------------------------
# 6. SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("🔍 DataLens")
st.sidebar.caption("DATA INTELLIGENCE PLATFORM")

selected_page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Data Profiling",
        "Column Statistics",
        "Data Cleaning",
        "Cleaning Report",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Version 2.0 | DataLens")


# --------------------------------------------------
# 7. DATASET UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv", "xlsx"],
)


# --------------------------------------------------
# 8. DATASET PROCESSING
# --------------------------------------------------

if uploaded_file is not None:

    try:
        # Read uploaded file bytes and identify the dataset.
        file_bytes = uploaded_file.getvalue()
        file_id = hashlib.sha256(file_bytes).hexdigest()

        # Reset results when a different dataset is uploaded.
        if st.session_state.get("active_file_id") != file_id:
            st.session_state["active_file_id"] = file_id
            st.session_state.pop("cleaned_df", None)
            st.session_state.pop("cleaning_report", None)
            st.session_state.pop("cleaned_excel_bytes", None)
            st.session_state.pop("cleaned_csv_bytes", None)
            st.session_state.pop("sample_values_selected_column", None)
            st.session_state.pop("sample_values_column_choice", None)

        # --------------------------------------------------
        # LOAD DATASET AND ANALYSIS (CACHED BY FILE CONTENT)
        # --------------------------------------------------

        with st.spinner(
            "📂 DataLens is loading and analysing your dataset..."
        ):
            df, profile, type_info = load_and_analyze_dataset(
                file_bytes,
                uploaded_file.name,
            )

        # Validate dataset structure.
        if len(df.columns) == 0:
            st.error("The uploaded dataset contains no columns.")

        elif df.empty:
            st.error("The uploaded dataset contains no records.")

        else:
            # --------------------------------------------------
            # 9. PREPARE LIGHTWEIGHT DATASET METRICS
            # --------------------------------------------------

            # The expensive file parsing and profiling above are cached.
            # These small display metrics are recalculated from the cached
            # DataFrame so navigation remains responsive.
            total_missing = sum(profile["missing_values"].values())
            total_cells = df.shape[0] * df.shape[1]
            completeness = (
                (total_cells - total_missing) / total_cells * 100
            )
            incomplete_percentage = 100 - completeness
            duplicate_percentage = profile["duplicate_rows"] / len(df) * 100
            unique_percentage = 100 - duplicate_percentage

            missing_df = pd.DataFrame(
                {
                    "Column": list(profile["missing_values"].keys()),
                    "Missing Values": list(profile["missing_values"].values()),
                }
            )

            missing_percentage_df = pd.DataFrame(
                {
                    "Column": df.columns,
                    "Missing Values": df.isnull().sum().values,
                    "Missing Percentage": (
                        df.isnull().sum().values / len(df) * 100
                    ),
                }
            )

            st.success(
                f"Successfully loaded: {uploaded_file.name}"
            )

            # --------------------------------------------------
            # 10. OVERVIEW PAGE
            # --------------------------------------------------

            if selected_page == "Overview":

                st.header("Dataset Overview")

                # KPI cards.
                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Total Rows",
                    f"{profile['total_rows']:,}",
                )

                col2.metric(
                    "Total Columns",
                    profile["total_columns"],
                )

                col3.metric(
                    "Missing Values",
                    total_missing,
                )

                col4.metric(
                    "Duplicate Rows",
                    profile["duplicate_rows"],
                )

                st.divider()

                # --------------------------------------------------
                # DATA QUALITY INSIGHTS
                # --------------------------------------------------

                st.subheader("Data Quality Insights")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Data Completeness**")

                    fig_completeness = create_quality_chart(
                        good_value=completeness,
                        issue_value=incomplete_percentage,
                        good_label="Complete",
                        issue_label="Incomplete",
                    )

                    st.plotly_chart(
                        fig_completeness,
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )

                    st.caption(
                        f"🟢 Complete: {completeness:.2f}% | "
                        f"🔴 Incomplete: {incomplete_percentage:.2f}%"
                    )

                with col2:
                    st.markdown("**Duplicate-Free Records**")

                    fig_duplicates = create_quality_chart(
                        good_value=unique_percentage,
                        issue_value=duplicate_percentage,
                        good_label="Unique",
                        issue_label="Duplicates",
                    )

                    st.plotly_chart(
                        fig_duplicates,
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )

                    st.caption(
                        f"🟢 Unique: {unique_percentage:.2f}% | "
                        f"🔴 Duplicates: {duplicate_percentage:.2f}%"
                    )

                st.divider()

                # --------------------------------------------------
                # MISSING VALUES CHART
                # --------------------------------------------------

                st.subheader("Missing Values by Column")

                chart_missing_df = missing_df[
                    missing_df["Missing Values"] > 0
                ]

                if not chart_missing_df.empty:
                    fig = px.bar(
                        chart_missing_df,
                        x="Column",
                        y="Missing Values",
                        title="Missing Values Distribution",
                        text="Missing Values",
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )
                else:
                    st.success(
                        "Excellent! No missing values detected."
                    )

                # --------------------------------------------------
                # DATASET PREVIEW
                # --------------------------------------------------

                st.subheader("Dataset Preview")

                st.dataframe(
                    df.head(10),
                    use_container_width=True,
                )

            # --------------------------------------------------
            # 11. DATA PROFILING PAGE
            # --------------------------------------------------

            elif selected_page == "Data Profiling":

                st.header("Data Profiling")

                st.write(
                    "Explore the structure and quality "
                    "of individual columns."
                )

                # Column information.
                st.subheader("Column Information")

                st.dataframe(
                    type_info,
                    use_container_width=True,
                    hide_index=True,
                )

                st.divider()

                # --------------------------------------------------
                # DATA TYPE DISTRIBUTION
                # --------------------------------------------------

                st.subheader("Data Type Distribution")

                dtype_df = (
                    type_info["Data_Type"]
                    .value_counts()
                    .reset_index()
                )

                dtype_df.columns = [
                    "Data Type",
                    "Column Count",
                ]

                fig = px.pie(
                    dtype_df,
                    names="Data Type",
                    values="Column Count",
                    hole=0.45,
                    title="Column Data Types",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                st.divider()

                # --------------------------------------------------
                # MISSING VALUE ANALYSIS
                # --------------------------------------------------

                st.subheader("Missing Value Analysis")

                # Display missing-value counts by column.
                st.dataframe(
                    missing_df,
                    use_container_width=True,
                    hide_index=True,
                )

                # Calculate and display the total number of missing cells.
                total_missing_cells = int(
                    missing_percentage_df["Missing Values"].sum()
                )

                st.metric(
                    "Total Missing Cells",
                    f"{total_missing_cells:,}",
                )

                # Create the missing-value percentage chart.
                fig = px.bar(
                    missing_percentage_df,
                    x="Column",
                    y="Missing Percentage",
                    title="Missing Values Percentage by Column",
                    custom_data=["Missing Values"],
                )

                # Show percentage labels and detailed hover information.
                fig.update_traces(
                    text=missing_percentage_df["Missing Percentage"].apply(
                        lambda value: f"{value:.2f}%"
                    ),
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Missing Values: %{customdata[0]:,}<br>"
                        "Missing Percentage: %{y:.2f}%"
                        "<extra></extra>"
                    ),
                )

                # Format the vertical axis as percentages.
                fig.update_layout(
                    yaxis=dict(
                        title="Missing Values (%)",
                        ticksuffix="%",
                        tickformat=".2f",
                        rangemode="tozero",
                    ),
                    xaxis_title="Column",
                    showlegend=False,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            # --------------------------------------------------
            # 12. COLUMN-LEVEL STATISTICS
            # --------------------------------------------------

            elif selected_page == "Column Statistics":

                st.header("Column-Level Statistics")
                st.write(
                    "Inspect detailed descriptive statistics and value "
                    "distribution for any column in your dataset."
                )

                selected_stat_column = st.selectbox(
                    "Select a column",
                    options=df.columns.tolist(),
                    key="column_statistics_selector",
                )

                series = df[selected_stat_column]
                non_null = int(series.notna().sum())
                missing = int(series.isna().sum())
                total = int(len(series))
                unique_count = int(series.nunique(dropna=True))
                missing_pct = (missing / total * 100) if total else 0.0
                unique_pct = (unique_count / non_null * 100) if non_null else 0.0

                st.subheader(f"Column profile: {selected_stat_column}")
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Data Type", str(series.dtype))
                m2.metric("Non-null", f"{non_null:,}")
                m3.metric("Missing", f"{missing:,}", f"{missing_pct:.2f}%")
                m4.metric("Unique Values", f"{unique_count:,}")
                m5.metric("Unique %", f"{unique_pct:.2f}%")

                st.divider()
                left, right = st.columns(2)

                if pd.api.types.is_numeric_dtype(series.dtype):
                    numeric = pd.to_numeric(series, errors="coerce").dropna()
                    with left:
                        st.markdown("**Numeric statistics**")
                        numeric_stats = pd.DataFrame({
                            "Statistic": ["Mean", "Median", "Standard deviation", "Minimum", "25th percentile", "50th percentile", "75th percentile", "Maximum", "Skewness"],
                            "Value": [
                                numeric.mean() if not numeric.empty else np.nan,
                                numeric.median() if not numeric.empty else np.nan,
                                numeric.std() if len(numeric) > 1 else np.nan,
                                numeric.min() if not numeric.empty else np.nan,
                                numeric.quantile(0.25) if not numeric.empty else np.nan,
                                numeric.quantile(0.50) if not numeric.empty else np.nan,
                                numeric.quantile(0.75) if not numeric.empty else np.nan,
                                numeric.max() if not numeric.empty else np.nan,
                                numeric.skew() if len(numeric) > 2 else np.nan,
                            ],
                        })
                        st.dataframe(numeric_stats, use_container_width=True, hide_index=True)
                    with right:
                        st.markdown("**Value distribution**")
                        if not numeric.empty:
                            fig_stats = px.histogram(
                                x=numeric, nbins=30,
                                labels={"x": selected_stat_column, "count": "Frequency"},
                                title=f"Distribution of {selected_stat_column}",
                            )
                            st.plotly_chart(fig_stats, use_container_width=True)
                        else:
                            st.info("No numeric values available for this column.")

                elif pd.api.types.is_datetime64_any_dtype(series.dtype):
                    dates = pd.to_datetime(series, errors="coerce").dropna()
                    with left:
                        st.markdown("**Date statistics**")
                        date_stats = pd.DataFrame({
                            "Statistic": ["Earliest date", "Latest date", "Date range (days)"],
                            "Value": [
                                str(dates.min()) if not dates.empty else "—",
                                str(dates.max()) if not dates.empty else "—",
                                (dates.max() - dates.min()).days if not dates.empty else "—",
                            ],
                        })
                        st.dataframe(date_stats, use_container_width=True, hide_index=True)
                    with right:
                        st.markdown("**Values over time**")
                        if not dates.empty:
                            date_counts = dates.dt.to_period("M").astype(str).value_counts().sort_index().reset_index()
                            date_counts.columns = ["Month", "Count"]
                            fig_stats = px.line(date_counts, x="Month", y="Count", markers=True, title="Records by month")
                            st.plotly_chart(fig_stats, use_container_width=True)
                        else:
                            st.info("No valid date values available for this column.")

                else:
                    non_null_values = series.dropna().astype(str)
                    value_counts = non_null_values.value_counts().head(15).reset_index()
                    value_counts.columns = ["Value", "Frequency"]
                    with left:
                        st.markdown("**Categorical statistics**")
                        mode_value = non_null_values.mode().iloc[0] if not non_null_values.empty else "—"
                        categorical_stats = pd.DataFrame({
                            "Statistic": ["Most frequent value", "Frequency of most frequent value", "Distinct values", "Most frequent value %"],
                            "Value": [
                                mode_value,
                                int(non_null_values.value_counts().iloc[0]) if not non_null_values.empty else 0,
                                unique_count,
                                (non_null_values.value_counts().iloc[0] / non_null * 100) if non_null else 0,
                            ],
                        })
                        st.dataframe(categorical_stats, use_container_width=True, hide_index=True)
                    with right:
                        st.markdown("**Top values**")
                        if not value_counts.empty:
                            fig_stats = px.bar(value_counts, x="Frequency", y="Value", orientation="h", title="Top 15 values")
                            fig_stats.update_layout(yaxis={"categoryorder": "total ascending"})
                            st.plotly_chart(fig_stats, use_container_width=True)
                        else:
                            st.info("No non-missing values available for this column.")

                st.divider()
                with st.expander("View sample values"):
                    st.dataframe(series.head(20).to_frame(name=selected_stat_column), use_container_width=True)

            # --------------------------------------------------
            # 13. DATA CLEANING STUDIO
            # --------------------------------------------------

            elif selected_page == "Data Cleaning":

                st.header("Data Cleaning Studio")

                st.write(
                    "Configure cleaning operations and transform "
                    "your dataset using the DataLens engine."
                )

                st.divider()

                # --------------------------------------------------
                # DUPLICATE REMOVAL
                # --------------------------------------------------

                st.subheader("1. Duplicate Removal")

                remove_duplicates = st.checkbox(
                    "Remove duplicate rows",
                    value=True,
                    help="Keep the first occurrence of duplicate rows.",
                )

                # --------------------------------------------------
                # MISSING VALUE HANDLING
                # --------------------------------------------------

                st.subheader("2. Missing Value Handling")

                missing_strategy = st.selectbox(
                    "Select missing-value strategy",
                    options=[
                        "drop",
                        "mean",
                        "median",
                    ],
                    format_func=lambda x: {
                        "drop": "Drop rows containing missing values",
                        "mean": (
                            "Replace missing numeric values with mean"
                        ),
                        "median": (
                            "Replace missing numeric values with median"
                        ),
                    }[x],
                )

                # --------------------------------------------------
                # DATA TYPE CONVERSION
                # --------------------------------------------------

                st.subheader("3. Data Type Conversion")

                enable_conversion = st.checkbox(
                    "Enable data type conversion"
                )

                conversions = {}
                integer_rounding = {}
                datetime_formats = {}

                if enable_conversion:

                    selected_columns = st.multiselect(
                        "Select one or more columns",
                        options=df.columns.tolist(),
                        help=(
                            "You can configure a different target data type "
                            "for each selected column."
                        ),
                    )

                    if selected_columns:
                        st.caption(
                            "Choose the target data type for each column."
                        )

                        for selected_column in selected_columns:
                            target_type = st.selectbox(
                                f"Target data type — {selected_column}",
                                options=[
                                    "int",
                                    "float",
                                    "str",
                                    "datetime",
                                ],
                                key=f"conversion_type_{selected_column}",
                            )

                            conversions[selected_column] = target_type

                            if target_type == "datetime":
                                selected_date_format = st.selectbox(
                                    f"Date format — {selected_column}",
                                    options=[
                                        "auto",
                                        "DD-MM-YYYY",
                                        "MM-DD-YYYY",
                                        "YYYY-MM-DD",
                                    ],
                                    format_func=lambda value: {
                                        "auto": "Auto detect",
                                        "DD-MM-YYYY": "DD-MM-YYYY (e.g. 25-12-2026)",
                                        "MM-DD-YYYY": "MM-DD-YYYY (e.g. 12-25-2026)",
                                        "YYYY-MM-DD": "YYYY-MM-DD (e.g. 2026-12-25)",
                                    }[value],
                                    key=f"datetime_format_{selected_column}",
                                    help=(
                                        "Choose the source date format. Use Auto detect "
                                        "when the column contains consistently recognizable dates."
                                    ),
                                )
                                datetime_formats[selected_column] = selected_date_format

                                # Show source values before conversion so users can
                                # verify that the selected format matches the data.
                                source_dates = (
                                    df[selected_column]
                                    .dropna()
                                    .astype(str)
                                    .head(8)
                                )
                                st.caption(
                                    f"Date preview — original values from **{selected_column}**"
                                )

                                if source_dates.empty:
                                    st.info(
                                        "This column has no non-missing values to preview."
                                    )
                                else:
                                    format_map = {
                                        "DD-MM-YYYY": "%d-%m-%Y",
                                        "MM-DD-YYYY": "%m-%d-%Y",
                                        "YYYY-MM-DD": "%Y-%m-%d",
                                    }
                                    if selected_date_format == "auto":
                                        parsed_preview = pd.to_datetime(
                                            source_dates,
                                            format="mixed",
                                            dayfirst=True,
                                            errors="coerce",
                                        )
                                    else:
                                        parsed_preview = pd.to_datetime(
                                            source_dates,
                                            format=format_map[selected_date_format],
                                            errors="coerce",
                                        )

                                    preview_df = pd.DataFrame({
                                        "Original value": source_dates.values,
                                        "Converted preview": parsed_preview.dt.strftime(
                                            "%Y-%m-%d"
                                        ).fillna("Invalid for selected format").values,
                                    })
                                    st.dataframe(
                                        preview_df,
                                        use_container_width=True,
                                        hide_index=True,
                                    )

                                    invalid_count = int(parsed_preview.isna().sum())
                                    if invalid_count:
                                        st.warning(
                                            f"{invalid_count} of the {len(source_dates)} preview values "
                                            f"do not match **{selected_date_format}**. "
                                            "Check the source values and choose the matching format "
                                            "before running cleaning."
                                        )

                                        # Suggest an alternative only when a date
                                        # component makes the format unambiguous.
                                        suggested_format = None
                                        for raw_value in source_dates:
                                            parts = str(raw_value).replace("/", "-").split("-")
                                            if len(parts) == 3:
                                                try:
                                                    first, second = int(parts[0]), int(parts[1])
                                                except ValueError:
                                                    continue
                                                if first > 12 and 1 <= second <= 12:
                                                    suggested_format = "DD-MM-YYYY"
                                                    break
                                                if second > 12 and 1 <= first <= 12:
                                                    suggested_format = "MM-DD-YYYY"
                                                    break
                                        if suggested_format and suggested_format != selected_date_format:
                                            st.info(
                                                f"Possible format mismatch: the values suggest "
                                                f"**{suggested_format}**. This is a suggestion only; "
                                                "DataLens will not change your selection automatically."
                                            )
                                    else:
                                        st.success(
                                            f"The preview values are compatible with **{selected_date_format}**."
                                        )

                            if target_type == "int":
                                integer_rounding[selected_column] = st.selectbox(
                                    f"Integer conversion method — {selected_column}",
                                    options=["round", "floor", "ceil"],
                                    format_func=lambda method: {
                                        "round": "Round to nearest integer (default)",
                                        "floor": "Floor (round down)",
                                        "ceil": "Ceil (round up)",
                                    }[method],
                                    key=f"integer_rounding_{selected_column}",
                                    help=(
                                        "Choose how decimal values are handled "
                                        "before converting this column to an integer."
                                    ),
                                )

                        conversion_summary = " | ".join(
                            f"{column} → {target_type}"
                            for column, target_type in conversions.items()
                        )

                        st.info(
                            f"Configured conversions: {conversion_summary}"
                        )
                    else:
                        st.info(
                            "Select at least one column to configure conversions."
                        )

                st.divider()

                # --------------------------------------------------
                # EXECUTE CLEANING WITH STATUS FEEDBACK
                # --------------------------------------------------

                st.subheader("4. Execute Cleaning")

                if st.button(
                    "Run Data Cleaning",
                    type="primary",
                    use_container_width=True,
                ):

                    # Remove previous results before starting a new run.
                    # This prevents users from exporting stale results
                    # if the new cleaning operation fails.
                    st.session_state.pop("cleaned_df", None)
                    st.session_state.pop("cleaning_report", None)
                    st.session_state.pop("cleaned_excel_bytes", None)
                    st.session_state.pop("cleaned_csv_bytes", None)

                    try:
                        with st.status(
                            "DataLens is cleaning your dataset...",
                            expanded=True,
                        ) as status:

                            status.write(
                                "Validating cleaning configuration..."
                            )

                            status.write(
                                "Applying cleaning operations..."
                            )

                            # Prepare a separate input copy for integer conversions.
                            # This prevents unsafe float64-to-int64 casts while
                            # preserving the original uploaded DataFrame.
                            conversion_input_df = df.copy(deep=True)

                            for column, method in integer_rounding.items():
                                try:
                                    numeric_values = pd.to_numeric(
                                        conversion_input_df[column],
                                        errors="raise",
                                    )
                                except (TypeError, ValueError) as conversion_error:
                                    raise ValueError(
                                        f"Column '{column}' contains values that "
                                        "cannot be interpreted as numbers. "
                                        "Please clean those values before integer conversion."
                                    ) from conversion_error

                                if method == "round":
                                    # Round halves away from zero (e.g. 2.5 -> 3, -2.5 -> -3).
                                    rounded_values = (
                                        np.sign(numeric_values)
                                        * np.floor(np.abs(numeric_values) + 0.5)
                                    )
                                elif method == "floor":
                                    rounded_values = np.floor(numeric_values)
                                else:  # ceil
                                    rounded_values = np.ceil(numeric_values)

                                conversion_input_df[column] = rounded_values

                            # Mean imputation can produce fractional values.
                            # Pandas nullable Int64 columns cannot store those
                            # values, so promote affected integer columns to
                            # Float64 before the pipeline performs imputation.
                            # This preserves the exact mean instead of rounding
                            # it or failing with an Int64 assignment error.
                            effective_conversions = (
                                dict(conversions) if conversions else {}
                            )
                            mean_promoted_columns = []

                            if missing_strategy == "mean":
                                for column in conversion_input_df.columns:
                                    target_type = effective_conversions.get(column)
                                    is_integer_target = target_type == "int"
                                    is_integer_source = pd.api.types.is_integer_dtype(
                                        conversion_input_df[column].dtype
                                    )
                                    has_missing = conversion_input_df[column].isna().any()

                                    if has_missing and (is_integer_source or is_integer_target):
                                        if is_integer_target:
                                            # A fractional mean cannot be represented
                                            # by an integer target without losing precision.
                                            effective_conversions[column] = "float"
                                        else:
                                            conversion_input_df[column] = (
                                                pd.to_numeric(
                                                    conversion_input_df[column],
                                                    errors="raise",
                                                ).astype("Float64")
                                            )
                                        mean_promoted_columns.append(column)

                            if mean_promoted_columns:
                                st.warning(
                                    "Mean imputation can produce decimal values. "
                                    "To preserve the exact mean, these integer columns "
                                    "will be stored as floating-point columns: "
                                    + ", ".join(mean_promoted_columns)
                                )

                            cleaned_df, cleaning_report = clean_dataset(
                                df=conversion_input_df,
                                remove_duplicate_rows=remove_duplicates,
                                missing_strategy=missing_strategy,
                                conversions=(
                                    effective_conversions if effective_conversions else None
                                ),
                                datetime_formats=(
                                    datetime_formats if datetime_formats else None
                                ),
                            )

                            status.write(
                                "Preparing cleaned dataset and report..."
                            )

                            # Store only successful results.
                            st.session_state["cleaned_df"] = cleaned_df
                            st.session_state["cleaning_report"] = (
                                cleaning_report
                            )

                            status.update(
                                label="Cleaning completed successfully!",
                                state="complete",
                                expanded=False,
                            )

                        st.success(
                            "Dataset cleaned successfully!"
                        )

                    except Exception as e:
                        st.error(
                            f"Cleaning failed: {str(e)}"
                        )

                # --------------------------------------------------
                # CLEANING RESULTS
                # --------------------------------------------------

                if "cleaned_df" in st.session_state:

                    cleaned_df = st.session_state["cleaned_df"]
                    report = st.session_state["cleaning_report"]

                    st.divider()

                    st.subheader("Cleaning Summary")

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric(
                        "Original Rows",
                        report["original_rows"],
                    )

                    col2.metric(
                        "Final Rows",
                        report["final_rows"],
                        delta=(
                            report["final_rows"]
                            - report["original_rows"]
                        ),
                    )

                    col3.metric(
                        "Duplicates Removed",
                        report["duplicates_removed"],
                    )

                    col4.metric(
                        "Missing Values Handled",
                        report["missing_values_handled"],
                    )

                    # --------------------------------------------------
                    # BEFORE AND AFTER COMPARISON
                    # --------------------------------------------------

                    st.subheader("Before vs After Cleaning")

                    tab1, tab2 = st.tabs(
                        [
                            "Original Dataset",
                            "Cleaned Dataset",
                        ]
                    )

                    with tab1:
                        # Preserve the original dataset as uploaded.
                        st.dataframe(
                            df,
                            use_container_width=True,
                        )

                    with tab2:
                        # Explicitly identify every floating-point column,
                        # including Pandas nullable Float32/Float64 types.
                        # Streamlit displays these values with exactly two
                        # decimal places (for example, 25.00 or 45000.50).
                        float_columns = [
                            column
                            for column in cleaned_df.columns
                            if pd.api.types.is_float_dtype(
                                cleaned_df[column].dtype
                            )
                        ]

                        float_column_config = {
                            column: st.column_config.NumberColumn(
                                label=column,
                                format="%.2f",
                            )
                            for column in float_columns
                        }

                        st.dataframe(
                            cleaned_df,
                            use_container_width=True,
                            column_config=float_column_config,
                        )

                        # Make it easy to verify that conversions were applied.
                        with st.expander("Verify column data types"):
                            dtype_info = pd.DataFrame(
                                {
                                    "Column": cleaned_df.columns,
                                    "Data Type": [
                                        str(dtype)
                                        for dtype in cleaned_df.dtypes
                                    ],
                                }
                            )

                            st.dataframe(
                                dtype_info,
                                use_container_width=True,
                                hide_index=True,
                            )

                            st.markdown("**Inspect converted sample values**")

                            # This selector only changes which column is previewed.
                            # It never replaces the uploaded dataset, clears the
                            # cleaning result, or starts another cleaning run.
                            valid_columns = cleaned_df.columns.tolist()
                            previous_sample_column = st.session_state.get(
                                "sample_values_selected_column", valid_columns[0]
                            )
                            if previous_sample_column not in valid_columns:
                                previous_sample_column = valid_columns[0]

                            sample_column = st.selectbox(
                                "Choose a column to inspect",
                                options=valid_columns,
                                index=valid_columns.index(previous_sample_column),
                                key="sample_values_column_choice",
                            )
                            st.session_state["sample_values_selected_column"] = (
                                sample_column
                            )

                            st.caption(
                                f"Showing the first 10 values from **{sample_column}** "
                                f"(data type: **{cleaned_df[sample_column].dtype}**)."
                            )

                            sample_values = cleaned_df[[sample_column]].head(10).copy()
                            sample_values.insert(
                                0,
                                "Row",
                                sample_values.index,
                            )

                            sample_column_config = {}
                            if pd.api.types.is_float_dtype(
                                cleaned_df[sample_column].dtype
                            ):
                                sample_column_config[sample_column] = (
                                    st.column_config.NumberColumn(
                                        label=sample_column,
                                        format="%.2f",
                                    )
                                )

                            st.dataframe(
                                sample_values,
                                use_container_width=True,
                                hide_index=True,
                                column_config=sample_column_config,
                            )

                    # --------------------------------------------------
                    # EXPORT CLEANED DATASET
                    # --------------------------------------------------

                    st.divider()

                    st.subheader("Export Cleaned Dataset")

                    col1, col2 = st.columns(2)

                    # Prepare CSV bytes once per cleaning run. The download
                    # control is green because the file is immediately ready.
                    if "cleaned_csv_bytes" not in st.session_state:
                        st.session_state["cleaned_csv_bytes"] = cleaned_df.to_csv(
                            index=False
                        ).encode("utf-8")

                    with col1:
                        with st.container(key="csv_download_ready"):
                            st.download_button(
                                label="✓ CSV Ready — Download",
                                data=st.session_state["cleaned_csv_bytes"],
                                file_name="datalens_cleaned.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )

                    with col2:
                        # Excel generation is intentionally on-demand. Once
                        # prepared, the same control becomes a green download
                        # button and the workbook remains cached in session.
                        if "cleaned_excel_bytes" not in st.session_state:
                            if st.button(
                                "Prepare Excel",
                                use_container_width=True,
                                key="prepare_cleaned_excel",
                            ):
                                try:
                                    with st.spinner("Preparing Excel workbook..."):
                                        excel_buffer = io.BytesIO()
                                        with pd.ExcelWriter(
                                            excel_buffer,
                                            engine="openpyxl",
                                        ) as writer:
                                            cleaned_df.to_excel(
                                                writer,
                                                index=False,
                                                sheet_name="Cleaned Data",
                                            )
                                        st.session_state["cleaned_excel_bytes"] = (
                                            excel_buffer.getvalue()
                                        )
                                    st.rerun()
                                except ImportError:
                                    st.error(
                                        "Excel export requires openpyxl. Run: "
                                        "python -m pip install openpyxl"
                                    )
                                except Exception as export_error:
                                    st.error(
                                        f"Could not prepare the Excel file: {export_error}"
                                    )
                        else:
                            with st.container(key="excel_download_ready"):
                                st.download_button(
                                    label="✓ Excel Ready — Download",
                                    data=st.session_state["cleaned_excel_bytes"],
                                    file_name="datalens_cleaned.xlsx",
                                    mime=(
                                        "application/vnd.openxmlformats-officedocument."
                                        "spreadsheetml.sheet"
                                    ),
                                    use_container_width=True,
                                )

            # --------------------------------------------------
            # 14. CLEANING REPORT EXPORT
            # --------------------------------------------------

            elif selected_page == "Cleaning Report":

                st.header("Cleaning Report")
                st.write(
                    "Review the latest cleaning run and export a standalone "
                    "report in Excel or PDF format."
                )

                if "cleaned_df" not in st.session_state or "cleaning_report" not in st.session_state:
                    st.info("No cleaning report is available yet. Open **Data Cleaning**, configure your cleaning options, and run the cleaning process first.")
                else:
                    cleaned_df = st.session_state["cleaned_df"]
                    report = st.session_state["cleaning_report"]
                    original_rows = int(report.get("original_rows", len(df)))
                    final_rows = int(report.get("final_rows", len(cleaned_df)))
                    removed_rows = max(original_rows - final_rows, 0)
                    duplicates_removed = int(report.get("duplicates_removed", 0))
                    missing_handled = int(report.get("missing_values_handled", 0))
                    rows_retained_pct = (final_rows / original_rows * 100) if original_rows else 0.0

                    st.subheader("Cleaning run summary")
                    r1, r2, r3, r4 = st.columns(4)
                    r1.metric("Original Rows", f"{original_rows:,}")
                    r2.metric("Final Rows", f"{final_rows:,}")
                    r3.metric("Duplicates Removed", f"{duplicates_removed:,}")
                    r4.metric("Missing Values Handled", f"{missing_handled:,}")

                    st.progress(min(max(rows_retained_pct / 100, 0.0), 1.0))
                    st.caption(f"Rows retained: {rows_retained_pct:.2f}% | Rows removed overall: {removed_rows:,}")

                    summary_df = pd.DataFrame({
                        "Metric": ["Source file", "Original rows", "Final rows", "Rows removed overall", "Duplicates removed", "Missing values handled", "Rows retained (%)", "Original columns", "Final columns"],
                        "Value": [uploaded_file.name, original_rows, final_rows, removed_rows, duplicates_removed, missing_handled, round(rows_retained_pct, 2), len(df.columns), len(cleaned_df.columns)],
                    })

                    column_report_df = pd.DataFrame({
                        "Column": cleaned_df.columns,
                        "Original Data Type": [str(df[c].dtype) if c in df.columns else "—" for c in cleaned_df.columns],
                        "Final Data Type": [str(cleaned_df[c].dtype) for c in cleaned_df.columns],
                        "Original Missing": [int(df[c].isna().sum()) if c in df.columns else 0 for c in cleaned_df.columns],
                        "Final Missing": [int(cleaned_df[c].isna().sum()) for c in cleaned_df.columns],
                        "Final Unique Values": [int(cleaned_df[c].nunique(dropna=True)) for c in cleaned_df.columns],
                    })

                    st.subheader("Column-level outcome")
                    st.dataframe(column_report_df, use_container_width=True, hide_index=True)

                    st.divider()
                    st.subheader("Export cleaning report")
                    export_col1, export_col2 = st.columns(2)

                    with export_col1:
                        report_excel = io.BytesIO()
                        with pd.ExcelWriter(report_excel, engine="openpyxl") as writer:
                            summary_df.to_excel(writer, index=False, sheet_name="Cleaning Summary")
                            column_report_df.to_excel(writer, index=False, sheet_name="Column Outcomes")
                        st.download_button(
                            "Download Excel Report",
                            data=report_excel.getvalue(),
                            file_name="datalens_cleaning_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )

                    with export_col2:
                        try:
                            from reportlab.lib import colors
                            from reportlab.lib.pagesizes import A4
                            from reportlab.lib.styles import getSampleStyleSheet
                            from reportlab.lib.units import mm
                            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

                            pdf_buffer = io.BytesIO()
                            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
                            styles = getSampleStyleSheet()
                            story = [
                                Paragraph("DataLens — Cleaning Report", styles["Title"]),
                                Spacer(1, 8),
                                Paragraph(f"Source file: {uploaded_file.name}", styles["Normal"]),
                                Spacer(1, 12),
                            ]
                            pdf_summary = [["Metric", "Value"]] + [[str(row["Metric"]), str(row["Value"])] for _, row in summary_df.iterrows()]
                            summary_table = Table(pdf_summary, colWidths=[75*mm, 90*mm], repeatRows=1)
                            summary_table.setStyle(TableStyle([
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7C9D6")),
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
                                ("PADDING", (0, 0), (-1, -1), 6),
                            ]))
                            story.extend([summary_table, Spacer(1, 16), Paragraph("Column Outcomes", styles["Heading2"])])
                            pdf_columns = [[str(c) for c in column_report_df.columns]]
                            pdf_columns += [[str(value) for value in row] for row in column_report_df.fillna("—").itertuples(index=False, name=None)]
                            column_table = Table(pdf_columns, repeatRows=1)
                            column_table.setStyle(TableStyle([
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C9D6")),
                                ("FONTSIZE", (0, 0), (-1, -1), 7),
                                ("PADDING", (0, 0), (-1, -1), 4),
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
                            ]))
                            story.append(column_table)
                            doc.build(story)
                            st.download_button(
                                "Download PDF Report",
                                data=pdf_buffer.getvalue(),
                                file_name="datalens_cleaning_report.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        except ImportError:
                            st.warning("PDF export requires ReportLab. Add `reportlab` to requirements.txt and install it in your environment.")

    except Exception as e:
        st.error(
            f"Unable to process the uploaded file: {e}"
        )


# --------------------------------------------------
# 13. EMPTY STATE
# --------------------------------------------------

else:
    st.info(
        "Upload a CSV or Excel file to start exploring your data."
    )
