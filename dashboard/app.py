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
st.caption('DELHI AIR QUALITY PROJECT')
st.title('Pollution episode early warning')
st.write('See predicted AQI for the next 24 hours and when sustained pollution may start and end.')
st.info('Past-data demonstration: seven stations, with forecast dates in 2023. This is not live monitoring or an official CPCB advisory.')
OUT = ROOT/'experiments/results/v2'
COMBINED = ROOT/'experiments/results/combined_system'
ACTIVE = COMBINED if (COMBINED/'complete.json').exists() else OUT
DATA = ROOT/'data/processed/delhi_hourly_v2.parquet'
if not DATA.exists() or not (OUT/'run_manifest.json').exists():
    st.warning('Required data or saved results are missing. Follow the setup steps in the README.')
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
hour = st.sidebar.slider('Forecast starting hour · IST',0,23,12)
issued = pd.Timestamp(day)+pd.Timedelta(hours=hour)
st.sidebar.caption('2024–2025 pollutant files are downloaded but not used by these models yet.')
st.sidebar.caption('The forecast uses readings up to your chosen time. A backup model handles gaps in past readings. No forecast is made if the current AQI is missing.')
current = history.loc[history.timestamp == issued,'aqi'].iloc[0]
cols = st.columns(3)
cols[0].metric('Observed AQI',f'{current:.0f}' if pd.notna(current) else 'Unavailable')
cols[1].metric('CPCB category',category(current))
cols[2].metric('Forecast starts · IST',issued.strftime('%H:%M'))
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
            st.info('Some past readings are missing. A backup model trained for these gaps is being used, with its own prediction ranges.')
        signal = warning(trajectory,current)
        st.subheader(signal['risk'])
        st.caption('These labels describe the model forecast, not an official CPCB alert. An episode means AQI of at least 301 for three hours in a row.')
        horizons = st.columns(4)
        for col,h in zip(horizons,[1,6,12,24]):
            r = trajectory[trajectory.horizon == h].iloc[0]
            col.metric(f'+{h} hours',f'{r.prediction:.0f}',r['category'],delta_color='off')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trajectory.target_time,y=trajectory.upper,mode='lines',line=dict(width=0),showlegend=False))
        fig.add_trace(go.Scatter(x=trajectory.target_time,y=trajectory.lower,fill='tonexty',fillcolor='rgba(24,119,138,.13)',line=dict(width=0),name='Prediction range (90% target)'))
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
                values[0].metric('Predicted start',e.onset.strftime('%d %b %H:%M'))
                values[1].metric('Peak AQI',f'{e.peak_aqi:.0f}')
                values[2].metric('Peak time',e.peak_time.strftime('%H:%M'))
                values[3].metric('Duration',('≥' if e.left_censored or e.right_censored else '')+f'{e.duration_hours} hours')
                st.write('AQI expected below 301: '+(e.recovery.strftime('%d %b %H:%M IST') if e.recovery is not None else 'Not reached within the next 24 hours'))
                if e.left_censored:
                    st.caption('The episode begins at the first forecast hour; its true onset may be earlier.')
        st.caption('The shaded range aims to cover individual hourly readings; it is not the chance of an episode. Episode times are estimates within the next 24 hours.')
        st.download_button('Download this forecast',trajectory.to_csv(index=False),'forecast.csv','text/csv')
with tabs[1]:
    days = st.slider('History window · days',7,90,30)
    recent = history[(history.timestamp <= issued)&(history.timestamp > issued-pd.Timedelta(days=days))]
    st.plotly_chart(px.line(recent,x='timestamp',y='aqi',template='plotly_white',labels={'timestamp':'Observation time · IST','aqi':'AQI'}),width='stretch')
    st.caption('Gaps mean missing readings. Separate pollutant measurements are not model inputs yet because their timestamps need verification.')
with tabs[2]:
    st.write('MAE is average error in AQI points; lower is better. RMSE gives more weight to large errors. R² measures fit, not percentage accuracy. Precision measures correct warnings; recall measures detected episodes. F1 combines both.')
    results = pd.read_csv(OUT/'model_comparison.csv')
    if ACTIVE == COMBINED:
        st.subheader('Main and backup models · 2023 results')
        combined_results = pd.read_csv(COMBINED/'regression_metrics.csv')
        st.dataframe(combined_results[combined_results.station == station],hide_index=True,width='stretch')
        st.caption('Includes the backup model on dates with gaps in past readings, so this table covers more cases than the main-model table below.')
    st.subheader('Main models · cases with complete past readings')
    st.dataframe(results[(results.station == station)&(results.split == 'test_selected')].drop(columns=['station','split']),hide_index=True,width='stretch')
    st.caption('Models were chosen using average errors in January–June 2022. An earlier project version had already examined 2023, so a later, previously unused test period is still needed.')
    st.subheader('Episode detection and timing')
    events = pd.read_csv(ACTIVE/'event_metrics.csv')
    st.dataframe(events[(events.station == station)&(events.persistence == 3)].drop(columns='station'),hide_index=True,width='stretch')
    st.caption('Predictions made the same number of hours ahead are checked together. Each predicted episode can match one observed episode. Start and end errors require known boundaries.')
    warnings = pd.read_csv(ACTIVE/'warning_metrics.csv')
    st.subheader('Daily 24-hour warning performance')
    st.dataframe(warnings[warnings.station == station],hide_index=True,width='stretch')
    issued_path = ACTIVE/'issued_episode_metrics.csv'
    if issued_path.exists():
        st.subheader('Episode timing from one 24-hour forecast')
        issued_scores = pd.read_csv(issued_path).set_index('station').loc[station]
        st.caption('Each daily 24-hour forecast is checked separately. This measures individual episodes, while the warning table asks only whether any episode occurs.')
        st.dataframe(pd.DataFrame([issued_scores[['eligible_windows','evaluated_fraction','precision','recall','f1']]]),hide_index=True,width='stretch')
        timing = pd.DataFrame([{'quantity':label,'MAE (hours)':issued_scores[c],'eligible matched segments':issued_scores[c+'_n']}
                               for label,c in [('Onset','onset_error_hours'),('Peak within window','peak_error_hours'),('Duration','duration_error_hours'),('Recovery','recovery_error_hours')]])
        st.dataframe(timing,hide_index=True,width='stretch')
        st.caption('Start, duration and end errors exclude episodes whose boundaries are unknown. Small samples give limited evidence. A blank average means no suitable matches.')
    st.subheader('Which features does the model use?')
    importance = pd.read_csv(OUT/'feature_importance.csv')
    h = st.selectbox('Explain forecast horizon',[1,6,12,24])
    top = importance[importance.horizon == h].nlargest(12,'importance').sort_values('importance')
    st.plotly_chart(px.bar(top,x='importance',y='feature',orientation='h',template='plotly_white'),width='stretch')
    st.caption('Shows which inputs the main model uses most overall. It does not explain one specific forecast, the backup model or what causes pollution.')
    with st.expander('Detailed model and input comparisons'):
        st.dataframe(results[results.station == 'ALL'],hide_index=True,width='stretch')
with tabs[3]:
    snapshot = data[data.timestamp == issued][['station_name','aqi']].copy()
    snapshot['category'] = snapshot.aqi.map(category)
    st.subheader('Same-time observations across selected stations')
    st.dataframe(snapshot,hide_index=True,width='stretch')
    st.caption('Switch the station selector for each station’s own forecast and episode. No official city-wide AQI is inferred.')
    st.subheader('Checks for adding more stations')
    st.write('The forecast selector contains only stations with saved evaluated models. Other stations can have usable records without a validated forecast model yet.')
    expansion_path = ROOT/'reports/tables/station_expansion/candidates.csv'
    if expansion_path.exists():
        expansion = pd.read_csv(expansion_path)
        expansion['forecast_status'] = expansion.currently_modelled.map({True:'Available',False:'Not trained in current system'})
        st.dataframe(expansion[['station','forecast_status','recent_coverage_pct','coverage_candidate','reason']].rename(columns={
            'station':'Station','forecast_status':'Forecast status','recent_coverage_pct':'2019–2021 coverage (%)',
            'coverage_candidate':'Passes expansion coverage screen','reason':'Coverage assessment'}),hide_index=True,width='stretch')
        st.caption('Candidates need at least 85% of readings across 2019–2021, 70% in each year, two years of recorded hours and no conflicting readings. Passing this check does not prove forecast quality. The first record is not necessarily the station opening date.')
        st.download_button('Download station coverage audit',expansion.to_csv(index=False),'station_coverage_audit.csv','text/csv')
    else:
        st.info('Generate the expanded coverage audit with python -m src.analysis.reassess_stations.')
with tabs[4]:
    st.markdown((ROOT/'docs/methodology_guide.md').read_text(encoding='utf-8'))


