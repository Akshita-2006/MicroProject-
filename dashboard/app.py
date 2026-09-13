"""Delhi early-warning dashboard: historical research replay."""
from pathlib import Path
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from src.forecasting.service import forecast, warning
from src.episode_detection.timeline import category
st.set_page_config(page_title='Delhi | Pollution Early Warning',page_icon='🌫️',layout='wide')
st.markdown('''<style>
.stApp {background:#f4f7fa;color:#122b39} h1,h2,h3 {letter-spacing:-.035em}
[data-testid="stMetric"] {background:white;border:1px solid #dce5ea;border-radius:12px;padding:16px}
[data-testid="stMetricValue"] {font-size:1.3rem} [data-testid="stSidebar"] {background:#e8eff3} .block-container {padding-top:2.3rem}
</style>''',unsafe_allow_html=True)
st.caption('DELHI AIR QUALITY  /  RESEARCH OBSERVATORY')
st.title('Pollution episode early warning')
st.write('Explore a station forecast, its expected episode timeline, and the evidence behind it.')
st.info('Historical replay · 2017–2023 observations. Research prototype, not live monitoring or an official CPCB advisory.')
OUT = ROOT/'experiments/results/v2'
COMBINED = ROOT/'experiments/results/combined_system'
ACTIVE = COMBINED if (COMBINED/'complete.json').exists() else OUT
DATA = ROOT/'data/processed/delhi_hourly_v2.parquet'
if not DATA.exists() or not (OUT/'run_manifest.json').exists():
    st.warning('The corrected experiment run is not complete yet. Run python run_pipeline.py to build the system.')
    st.stop()
@st.cache_data
def load_data(data_revision):
    return pd.read_parquet(DATA)
@st.cache_data
def infer(station, issued, artifact_revision):
    p = load_data(DATA.stat().st_mtime_ns)
    return forecast(p[p.station_name == station],pd.Timestamp(issued))
data = load_data(DATA.stat().st_mtime_ns)
artifact_revision = tuple(path.stat().st_mtime_ns if path.exists() else None for path in [
    DATA,ROOT/'src/forecasting/service.py',OUT/'selection.json',
    ROOT/'experiments/results/missing_history_fallback/selection.json',COMBINED/'complete.json'])
stations = sorted(data.station_name.unique())
station = st.sidebar.selectbox('Monitoring station',stations,index=stations.index('Shadipur Delhi CPCB'))
history = data[data.station_name == station].sort_values('timestamp')
day = st.sidebar.date_input('Replay date',pd.Timestamp('2023-11-01').date(),min_value=pd.Timestamp('2023-01-01').date(),max_value=pd.Timestamp('2023-12-30').date())
hour = st.sidebar.slider('Issue hour · IST',0,23,12)
issued = pd.Timestamp(day)+pd.Timedelta(hours=hour)
st.sidebar.caption('Forecasts use observations through the issue time. A validated fallback can handle missing past values; missing current AQI causes abstention.')
current = history.loc[history.timestamp == issued,'aqi'].iloc[0]
cols = st.columns(3)
cols[0].metric('Observed AQI',f'{current:.0f}' if pd.notna(current) else 'Unavailable')
cols[1].metric('CPCB category',category(current))
cols[2].metric('Issued · IST',issued.strftime('%H:%M'))
st.caption(station+' · This station does not represent all of Delhi.')
tabs = st.tabs(['Forecast & episode','Historical trends','Model evidence','Station comparison','Methodology'])
with tabs[0]:
    try:
        trajectory = infer(station,str(issued),artifact_revision)
    except ValueError as error:
        st.warning(str(error))
        trajectory = None
    if trajectory is not None:
        if trajectory.route.eq('missing_history_fallback').any():
            st.info('Missing-history fallback: some past observations are unavailable. This model was trained for that condition, with separately calibrated intervals.')
        signal = warning(trajectory,current)
        st.subheader(signal['risk'])
        st.caption('Research warning states summarize sustained forecasts; they are not official CPCB alert levels.')
        horizons = st.columns(4)
        for col,h in zip(horizons,[1,6,12,24]):
            r = trajectory[trajectory.horizon == h].iloc[0]
            col.metric(f'+{h} hours',f'{r.prediction:.0f}',r['category'],delta_color='off')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trajectory.target_time,y=trajectory.upper,mode='lines',line=dict(width=0),showlegend=False))
        fig.add_trace(go.Scatter(x=trajectory.target_time,y=trajectory.lower,fill='tonexty',fillcolor='rgba(24,119,138,.13)',line=dict(width=0),name='Nominal 90% interval'))
        fig.add_trace(go.Scatter(x=trajectory.target_time,y=trajectory.prediction,mode='lines+markers',line=dict(color='#13798c',width=3),name='Forecast AQI'))
        fig.add_hline(y=301,line_dash='dash',line_color='#b96b31',annotation_text='Very Poor · 301')
        fig.update_layout(template='plotly_white',height=360,margin=dict(l=10,r=10,t=20,b=20),yaxis_title='AQI',xaxis_title='Target time · IST',legend=dict(orientation='h',y=1.15))
        st.plotly_chart(fig,width='stretch')
        if not signal['episodes']:
            st.success('No sustained episode predicted within the next 24 hours.')
            st.caption('This does not rule out isolated high values or an episode beyond the forecast window.')
        for i,e in enumerate(signal['episodes'],1):
            with st.container(border=True):
                st.subheader(f'Episode {i} · {e.severity}')
                values = st.columns(4)
                values[0].metric('Onset in forecast',e.onset.strftime('%d %b %H:%M'))
                values[1].metric('Peak AQI',f'{e.peak_aqi:.0f}')
                values[2].metric('Peak time',e.peak_time.strftime('%H:%M'))
                values[3].metric('Duration',('≥' if e.left_censored or e.right_censored else '')+f'{e.duration_hours} hours')
                st.write('Expected recovery: '+(e.recovery.strftime('%d %b %H:%M IST') if e.recovery is not None else 'Not observed within this forecast window'))
                if e.left_censored:
                    st.caption('The episode begins at the first forecast hour; its true onset may be earlier.')
        st.caption('Intervals are marginal calibration bands, not event probabilities. Timing is hourly and window-limited.')
        st.download_button('Download this forecast',trajectory.to_csv(index=False),'forecast.csv','text/csv')
with tabs[1]:
    days = st.slider('History window · days',7,90,30)
    recent = history[(history.timestamp <= issued)&(history.timestamp > issued-pd.Timedelta(days=days))]
    st.plotly_chart(px.line(recent,x='timestamp',y='aqi',template='plotly_white',labels={'timestamp':'Observation time · IST','aqi':'AQI'}),width='stretch')
    st.caption('Gaps are retained. Pollutant features are excluded from the primary model pending source timestamp verification.')
with tabs[2]:
    results = pd.read_csv(OUT/'model_comparison.csv')
    if ACTIVE == COMBINED:
        st.subheader('Combined system · retrospective 2023 test')
        combined_results = pd.read_csv(COMBINED/'regression_metrics.csv')
        st.dataframe(combined_results[combined_results.station == station],hide_index=True,width='stretch')
        st.caption('Includes primary forecasts and the validation-selected missing-history fallback. This is a broader population than the primary-model table below.')
    st.subheader('Primary models · complete-history test cases')
    st.dataframe(results[(results.station == station)&(results.split == 'test_selected')].drop(columns=['station','split']),hide_index=True,width='stretch')
    st.caption('Models were selected using January–June 2022 MAE. The inherited prototype already inspected the 2023 era; these are not pristine external-holdout results.')
    st.subheader('Episode detection and timing')
    events = pd.read_csv(ACTIVE/'event_metrics.csv')
    st.dataframe(events[(events.station == station)&(events.persistence == 3)].drop(columns='station'),hide_index=True,width='stretch')
    st.caption('Fixed-lead streams; one-to-one overlapping event matches. Timing errors concern matched events; censored endpoints are excluded.')
    warnings = pd.read_csv(ACTIVE/'warning_metrics.csv')
    st.subheader('Daily 24-hour warning performance')
    st.dataframe(warnings[warnings.station == station],hide_index=True,width='stretch')
    issued_path = ACTIVE/'issued_episode_metrics.csv'
    if issued_path.exists():
        st.subheader('Episode timing from one 24-hour forecast')
        issued_scores = pd.read_csv(issued_path).set_index('station').loc[station]
        st.caption('Same-origin episode segments, evaluated independently within each daily forecast window. These scores differ from binary warning presence.')
        st.dataframe(pd.DataFrame([issued_scores[['eligible_windows','evaluated_fraction','precision','recall','f1']]]),hide_index=True,width='stretch')
        timing = pd.DataFrame([{'quantity':label,'MAE (hours)':issued_scores[c],'eligible matched segments':issued_scores[c+'_n']}
                               for label,c in [('Onset','onset_error_hours'),('Peak within window','peak_error_hours'),('Duration','duration_error_hours'),('Recovery','recovery_error_hours')]])
        st.dataframe(timing,hide_index=True,width='stretch')
        st.caption('Censored endpoints are excluded from onset/duration/recovery errors. Small matched samples are weak evidence; a missing mean means no eligible matches.')
    st.subheader('Which features does the model use?')
    importance = pd.read_csv(OUT/'feature_importance.csv')
    h = st.selectbox('Explain forecast horizon',[1,6,12,24])
    top = importance[importance.horizon == h].nlargest(12,'importance').sort_values('importance')
    st.plotly_chart(px.bar(top,x='importance',y='feature',orientation='h',template='plotly_white'),width='stretch')
    st.caption('Global tree importance for the primary model; not a local explanation, fallback explanation, or evidence of causation.')
    with st.expander('Full baseline, model and feature-ablation results'):
        st.dataframe(results[results.station == 'ALL'],hide_index=True,width='stretch')
with tabs[3]:
    snapshot = data[data.timestamp == issued][['station_name','aqi']].copy()
    snapshot['category'] = snapshot.aqi.map(category)
    st.subheader('Same-time observations across selected stations')
    st.dataframe(snapshot,hide_index=True,width='stretch')
    st.caption('Switch the station selector for each station’s own forecast and episode. No official city-wide AQI is inferred.')
with tabs[4]:
    st.markdown((ROOT/'docs/methodology_v2.md').read_text(encoding='utf-8'))


