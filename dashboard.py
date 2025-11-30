import pandas as pd
import streamlit as st
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="MotoGP Telemetry DSS", layout="wide", page_icon="🏁")


@st.cache_data
def load_data(file_path):
    """Load and preprocess telemetry data"""
    df = pd.read_csv(file_path, sep=';')
    df.replace(-1, pd.NA, inplace=True)

    df['lap_time'] = pd.to_numeric(df['lap_time'], errors='coerce')
    df['lapNum'] = pd.to_numeric(df['lapNum'], errors='coerce')

    df = df[df['validBin'] == 1].copy()
    df = df.sort_values(['lapNum', 'binIndex']).reset_index(drop=True)

    df['display_time'] = df['lap_time'].copy()

    for lap in sorted(df['lapNum'].unique()):
        lap_mask = df['lapNum'] == lap
        lap_indices = df[lap_mask].index

        for i, idx in enumerate(lap_indices):
            if pd.isna(df.loc[idx, 'display_time']):
                df.loc[idx, 'display_time'] = i * 0.1

    return df


def check_alerts(row):
    alerts = []
    if pd.notna(row['rpm']) and row['rpm'] > 16000:
        alerts.append(("🔴 RPM Critical!", "error"))
    if pd.notna(row['brake_temp_0']) and row['brake_temp_0'] > 800:
        alerts.append(("🔥 Brake Overheat!", "warning"))
    if pd.notna(row['throttle']) and row['throttle'] > 0.95:
        alerts.append(("⚡ Full Throttle", "success"))
    if pd.notna(row['tyre_wear_0']) and row['tyre_wear_0'] > 0.7:
        alerts.append(("⚠️ Tire Critical", "warning"))
    return alerts


def create_speed_rpm_chart(df_slice):
    fig = make_subplots(rows=2, cols=1, subplot_titles=('Speed', 'RPM'), vertical_spacing=0.1)
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['velocity_X'],
                             mode='lines', line=dict(color='#00ccff', width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['rpm'],
                             mode='lines', line=dict(color='#ff3333', width=3)), row=2, col=1)
    fig.update_xaxes(title_text="Lap Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="m/s", row=1, col=1)
    fig.update_yaxes(title_text="RPM", row=2, col=1)
    fig.update_layout(height=450, showlegend=False, margin=dict(t=30, b=30, l=50, r=20))
    return fig


def create_throttle_brake_chart(df_slice):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['throttle'] * 100,
                             mode='lines', line=dict(color='#00ff00', width=3), fill='tozeroy', name='Throttle'))
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['brake_0'] * 100,
                             mode='lines', line=dict(color='#ff0000', width=3), fill='tozeroy', name='Brake'))
    fig.update_layout(title='Inputs', xaxis_title='Time (s)', yaxis_title='%',
                      height=280, yaxis=dict(range=[0, 100]), margin=dict(t=30, b=30))
    return fig


def create_gforce_chart(df_slice):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['gforce_X'],
                             mode='lines', line=dict(color='cyan', width=2), name='Lateral'))
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['gforce_Y'],
                             mode='lines', line=dict(color='orange', width=2), name='Long'))
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['gforce_Z'],
                             mode='lines', line=dict(color='purple', width=2), name='Vert'))
    fig.update_layout(title='G-Forces', xaxis_title='Time (s)', height=280, margin=dict(t=30, b=30))
    return fig


def create_tire_temp_chart(df_slice):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['brake_temp_0'],
                             mode='lines', line=dict(color='#ff6600', width=3), name='Front'))
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['brake_temp_1'],
                             mode='lines', line=dict(color='#ff0066', width=3), name='Rear'))
    fig.update_layout(title='Brake Temps', xaxis_title='Time (s)', height=280, margin=dict(t=30, b=30))
    return fig


def create_gear_chart(df_slice):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_slice['display_time'], y=df_slice['gear'],
                             mode='lines', line=dict(color='yellow', width=3, shape='hv')))
    fig.update_layout(title='Gear', xaxis_title='Time (s)', height=250,
                      yaxis=dict(tickmode='linear', tick0=1, dtick=1), margin=dict(t=30, b=30))
    return fig


def create_tire_wear_gauge(row):
    fig = go.Figure()
    wear_f = row['tyre_wear_0'] * 100 if pd.notna(row['tyre_wear_0']) else 0
    wear_r = row['tyre_wear_1'] * 100 if pd.notna(row['tyre_wear_1']) else 0

    fig.add_trace(go.Indicator(mode="gauge+number", value=wear_f, title={'text': "Front"},
                               gauge={'axis': {'range': [0, 100]},
                                      'bar': {
                                          'color': "darkred" if wear_f > 70 else "orange" if wear_f > 50 else "green"}},
                               domain={'x': [0, 0.45], 'y': [0, 1]}))
    fig.add_trace(go.Indicator(mode="gauge+number", value=wear_r, title={'text': "Rear"},
                               gauge={'axis': {'range': [0, 100]},
                                      'bar': {
                                          'color': "darkred" if wear_r > 70 else "orange" if wear_r > 50 else "green"}},
                               domain={'x': [0.55, 1], 'y': [0, 1]}))
    fig.update_layout(height=250, margin=dict(t=10, b=10))
    return fig


def main():
    st.title("🏁 MotoGP Live Telemetry")

    file_path = "data/SachenRing_M1_Rossi.csv"
    try:
        df = load_data(file_path)
    except Exception as e:
        st.error(f"❌ {e}")
        return

    # Sidebar
    st.sidebar.header("⚙️ Controls")
    update_interval = st.sidebar.slider("Update Every N Rows", 10, 100, 30)
    playback_speed = st.sidebar.slider("Playback Speed", 0.1, 2.0, 1.0, 0.1)

    laps_list = sorted(df['lapNum'].unique())
    st.sidebar.info(f"Laps: {laps_list}")
    st.sidebar.info(f"Rider: {df['carId'].iloc[0]}")
    st.sidebar.info(f"Track: {df['trackId'].iloc[0]}")

    # Controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Stream", type="primary", use_container_width=True):
            st.session_state.streaming = True
    with col2:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.streaming = False

    if 'streaming' not in st.session_state:
        st.session_state.streaming = False

    # Fixed containers
    metrics_container = st.empty()
    alerts_container = st.empty()
    st.markdown("---")
    progress_container = st.empty()

    chart_row1_col1 = st.empty()
    chart_row1_col2 = st.empty()

    chart_row2_col1 = st.empty()
    chart_row2_col2 = st.empty()

    chart_row3_col1 = st.empty()
    chart_row3_col2 = st.empty()

    # Streaming loop
    if st.session_state.streaming:
        for idx in range(0, len(df), update_interval):
            if not st.session_state.get('streaming', False):
                break

            end_idx = min(idx + update_interval, len(df))
            current_row = df.iloc[end_idx - 1]
            current_lap = int(current_row['lapNum']) if pd.notna(current_row['lapNum']) else 0

            # Get data for current lap only
            lap_data = df[df['lapNum'] == current_lap]
            display_data = lap_data[lap_data.index <= end_idx]

            if len(display_data) == 0:
                continue

            # Progress
            progress = end_idx / len(df)
            progress_container.progress(progress,
                                        text=f"Lap {current_lap} | {end_idx}/{len(df)} ({progress * 100:.0f}%)")

            # Metrics
            with metrics_container.container():
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("🏁 Lap", f"{current_lap}")
                c2.metric("🚀 Speed",
                          f"{current_row['velocity_X']:.1f}" if pd.notna(current_row['velocity_X']) else "N/A")
                c3.metric("⚙️ RPM", f"{current_row['rpm']:.0f}" if pd.notna(current_row['rpm']) else "N/A")
                c4.metric("🔧 Gear", f"{int(current_row['gear'])}" if pd.notna(current_row['gear']) else "N/A")
                c5.metric("⚡ Throttle",
                          f"{current_row['throttle'] * 100:.0f}%" if pd.notna(current_row['throttle']) else "0%")
                c6.metric("⏱️ Time",
                          f"{current_row['display_time']:.1f}s" if pd.notna(current_row['display_time']) else "N/A")

            # Alerts
            alerts = check_alerts(current_row)
            if alerts:
                with alerts_container.container():
                    acols = st.columns(len(alerts))
                    for i, (msg, atype) in enumerate(alerts):
                        with acols[i]:
                            if atype == "error":
                                st.error(msg, icon="🔴")
                            elif atype == "warning":
                                st.warning(msg, icon="⚠️")
                            else:
                                st.success(msg, icon="✅")
            else:
                alerts_container.empty()

            # Charts
            if len(display_data) > 5:
                with chart_row1_col1.container():
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.plotly_chart(create_speed_rpm_chart(display_data), use_container_width=True, key=f"sr_{idx}")
                    with col2:
                        st.plotly_chart(create_throttle_brake_chart(display_data), use_container_width=True,
                                        key=f"tb_{idx}")

                with chart_row2_col1.container():
                    col3, col4 = st.columns(2)
                    with col3:
                        st.plotly_chart(create_gforce_chart(display_data), use_container_width=True, key=f"gf_{idx}")
                    with col4:
                        st.plotly_chart(create_tire_temp_chart(display_data), use_container_width=True, key=f"tt_{idx}")

                with chart_row3_col1.container():
                    col5, col6 = st.columns(2)
                    with col5:
                        st.plotly_chart(create_gear_chart(display_data), use_container_width=True, key=f"gr_{idx}")
                    with col6:
                        st.plotly_chart(create_tire_wear_gauge(current_row), use_container_width=True, key=f"tw_{idx}")

            # Controlled delay
            time.sleep(playback_speed)

        progress_container.success("✅ Stream complete!")
        st.session_state.streaming = False


if __name__ == "__main__":
    main()
