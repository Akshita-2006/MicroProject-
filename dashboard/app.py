"""Delhi early-warning dashboard: historical research replay."""
from pathlib import Path
import sys
import re
import joblib
import numpy as np
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
def sync_pollutant_date():
    st.session_state.selected_date = st.session_state.pollutant_date
def sync_sidebar_date():
    """Keep the pollutant view on the same date when a source record exists."""
    selected = st.session_state.selected_date
    if selected >= pd.Timestamp('2024-01-01').date():
        st.session_state.pollutant_date = selected
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = pd.Timestamp('2023-11-01').date()
if 'pollutant_date' not in st.session_state:
    st.session_state.pollutant_date = pd.Timestamp('2024-01-01').date()
st.markdown('''<style>
.stApp {background:#f4f7fa;color:#122b39} h1,h2,h3 {letter-spacing:-.035em}
[data-testid="stMetric"] {background:white;border:1px solid #dce5ea;border-radius:12px;padding:16px}
[data-testid="stMetricValue"] {font-size:1.3rem} [data-testid="stSidebar"] {background:#e8eff3} .block-container {padding-top:2.3rem}
</style>''',unsafe_allow_html=True)
st.caption('DELHI AIR QUALITY PROJECT')
EXPANDED_OUT = ROOT/'experiments/results/all_eligible_30'
EXPANDED_DATA = ROOT/'data/processed/delhi_hourly_all_eligible.parquet'
USE_EXPANDED = (EXPANDED_OUT/'run_manifest.json').exists() and EXPANDED_DATA.exists()
EXPERIMENT = 'all_eligible_30' if USE_EXPANDED else 'v2'
OUT = EXPANDED_OUT if USE_EXPANDED else ROOT/'experiments/results/v2'
COMBINED = ROOT/'experiments/results/combined_system'
ACTIVE = OUT if USE_EXPANDED else (COMBINED if (COMBINED/'complete.json').exists() else OUT)
DATA = EXPANDED_DATA if USE_EXPANDED else ROOT/'data/processed/delhi_hourly_v2.parquet'
if not DATA.exists() or not (OUT/'run_manifest.json').exists():
    st.warning('Required data or saved results are missing. Follow the setup steps in the README.')
    st.stop()
@st.cache_data
def load_data(data_revision):
    return pd.read_parquet(DATA)
@st.cache_data
def load_pollutants(year):
    path = ROOT/f'data/interim/delhi_pollutants_{year}_source_release.parquet'
    if not path.exists():
        path = ROOT/f'data/interim/delhi_pollutants_{year}_unverified.parquet'
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()
def source_station_name(station, names):
    normalize = lambda text: re.sub(r'[^a-z0-9]', '', re.sub(r'\b(delhi|cpcb|dpcc|imd|iitm)\b', '', text.lower()))
    target = normalize(station)
    return next((name for name in names if normalize(str(name)) == target), None)
@st.cache_data
def load_concentration_panel():
    path = ROOT/'data/processed/delhi_concentrations_hourly_2017_2025.parquet'
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()
@st.cache_resource(show_spinner=False)
def load_concentration_model(path, revision):
    """Load each saved concentration model once per dashboard process."""
    return joblib.load(path)
def concentration_forecasts(station, issued):
    panel=load_concentration_panel()
    history=panel[(panel.station_name==station)&(panel.timestamp<=issued)].sort_values('timestamp').tail(73)
    if len(history)<73 or history.timestamp.iloc[-1] != issued:
        return pd.DataFrame()
    targets=['PM2.5 (µg/m³)','PM10 (µg/m³)','NO2 (µg/m³)','Ozone (µg/m³)','SO2 (µg/m³)','CO (mg/m³)','Benzene (µg/m³)']
    rows=[]
    for target in targets:
        if history[target].isna().any(): continue
        name=target.replace(' (µg/m³)','').replace(' (mg/m³)','').replace('.','').replace(' ','_')
        frame=history[['station_name','timestamp',target]].copy()
        for lag in [1,2,3,6,12,24,48,72]: frame[f'{name}_lag_{lag}']=frame[target].shift(lag)
        frame['hour_sin']=np.sin(2*np.pi*frame.timestamp.dt.hour/24); frame['hour_cos']=np.cos(2*np.pi*frame.timestamp.dt.hour/24)
        frame['month_sin']=np.sin(2*np.pi*(frame.timestamp.dt.month-1)/12); frame['month_cos']=np.cos(2*np.pi*(frame.timestamp.dt.month-1)/12)
        row=frame.tail(1).copy()
        safe=''.join(c if c.isalnum() else '_' for c in target)
        for h in [1,6,12,24]:
            artifact=ROOT/f'experiments/models/concentrations_2017_2025/{safe}_h{h}.joblib'
            if not artifact.exists(): continue
            saved=load_concentration_model(str(artifact), artifact.stat().st_mtime_ns)
            for feature in saved['features']:
                if feature.startswith('station_'): row[feature]=float(feature=='station_'+station)
            rows.append({'Pollutant':target,'Hours ahead':h,'Predicted concentration':float(saved['model'].predict(row[saved['features']])[0])})
    return pd.DataFrame(rows)
def concentration_table(predicted):
    table = predicted[predicted['Hours ahead'].isin([1, 6, 12, 24])].pivot(
        index='Pollutant', columns='Hours ahead', values='Predicted concentration'
    ).reindex(columns=[1, 6, 12, 24]).reset_index()
    return table.rename(columns={1: '+1 hour', 6: '+6 hours', 12: '+12 hours', 24: '+24 hours'}).round(2)
@st.cache_data
def infer(station, issued, artifact_revision):
    p = load_data(DATA.stat().st_mtime_ns)
    return forecast(p[p.station_name == station],pd.Timestamp(issued),experiment=EXPERIMENT)
data = load_data(DATA.stat().st_mtime_ns)
artifact_revision = tuple(path.stat().st_mtime_ns if path.exists() else None for path in [
    DATA,ROOT/'src/forecasting/service.py',OUT/'selection.json',
    ROOT/'experiments/results/missing_history_fallback/selection.json',COMBINED/'complete.json'])
stations = sorted(data.station_name.unique())
station = st.sidebar.selectbox('Monitoring station',stations,index=stations.index('Shadipur Delhi CPCB'))
history = data[data.station_name == station].sort_values('timestamp')
day = st.sidebar.date_input('Selected date',min_value=pd.Timestamp('2023-01-01').date(),max_value=pd.Timestamp('2025-12-31').date(),key='selected_date',on_change=sync_sidebar_date)
hour = st.sidebar.slider('Forecast starting hour · IST',0,23,12)
issued = pd.Timestamp(day)+pd.Timedelta(hours=hour)
aqi_mode = issued.year <= 2023
recent_concentration_forecast = concentration_forecasts(station, issued) if not aqi_mode else pd.DataFrame()
if aqi_mode:
    st.title('Pollution episode early warning')
    st.write('See predicted AQI for the next 24 hours and when sustained pollution may start and end.')
    st.info(('Historical AQI forecast demonstration: 30 Delhi stations, evaluated with 2023 observations.' if USE_EXPANDED else
             'Historical AQI forecast demonstration: seven Delhi stations, evaluated with 2023 observations.')+
            ' This is not live monitoring or an official CPCB advisory.')
    st.sidebar.caption('The forecast uses the historical AQI record. Newer pollutant readings are displayed only after their source details are checked.')
    st.sidebar.caption('The forecast uses readings up to your chosen time. A backup model handles gaps in past readings. No forecast is made if the current AQI is missing.')
    current_values = history.loc[history.timestamp == issued, 'aqi']
    current = current_values.iloc[0] if not current_values.empty else float('nan')
else:
    st.title('Pollution concentration forecast')
    st.write('See predicted pollutant concentrations for the next 24 hours at the selected station and time.')
    st.info('Past-data concentration forecast for 2024–2025. This is not live monitoring or an official CPCB advisory.')
    st.sidebar.caption('The selected station, date and hour are used for recorded concentrations and the next 24-hour concentration forecast.')
    current = float('nan')
cols = st.columns(3)
if aqi_mode:
    cols[0].metric('Observed AQI',f'{current:.0f}' if pd.notna(current) else 'Unavailable')
    cols[1].metric('CPCB category',category(current))
    cols[2].metric('Forecast starts · IST',issued.strftime('%H:%M'))
else:
    cols[0].metric('Selected date',issued.strftime('%d %b %Y'))
    cols[1].metric('Pollutant forecasts','Available' if not recent_concentration_forecast.empty else 'Unavailable')
    cols[2].metric('Forecast starts · IST',issued.strftime('%H:%M'))
st.caption(station+' · This station does not represent all of Delhi.')
tabs = st.tabs([('Forecast & episode' if aqi_mode else 'Concentration forecast'),
                ('AQI history' if aqi_mode else 'Concentration history'),
                'Pollutants','Model evidence','Station comparison','Methodology'])
with tabs[0]:
    trajectory = None
    if issued.year <= 2023:
        try:
            trajectory = infer(station,str(issued),artifact_revision)
        except ValueError:
            trajectory = None
    else:
        st.subheader('Pollutant forecast for the next 24 hours')
        concentration_view = recent_concentration_forecast
        if concentration_view.empty:
            st.info('A pollutant forecast needs 73 continuous recorded hours for every pollutant. This station or time does not have enough complete history.')
        else:
            st.dataframe(concentration_table(concentration_view), hide_index=True, width='stretch')
            st.caption('Each row is one pollutant. The four columns show all next-hour forecasts from the selected station, date and hour.')
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
    if aqi_mode:
        recent = history[(history.timestamp <= issued)&(history.timestamp > issued-pd.Timedelta(days=days))]
        st.plotly_chart(px.line(recent,x='timestamp',y='aqi',template='plotly_white',labels={'timestamp':'Observation time · IST','aqi':'AQI'}),width='stretch')
        st.caption('Gaps mean missing readings. Separate pollutant measurements are not model inputs in the historical AQI model.')
    else:
        panel = load_concentration_panel()
        available = [column for column in panel.columns if column not in ['station_name', 'timestamp']]
        pollutant = st.selectbox('Pollutant to display', available, key='concentration_history_pollutant')
        recent = panel[(panel.station_name == station) & (panel.timestamp <= issued) &
                       (panel.timestamp > issued-pd.Timedelta(days=days))]
        if recent.empty or recent[pollutant].dropna().empty:
            st.info('No recorded concentration history is available for this station, pollutant and selected period.')
        else:
            st.plotly_chart(px.line(recent,x='timestamp',y=pollutant,template='plotly_white',
                                    labels={'timestamp':'Observation time · IST', pollutant:'Recorded concentration'}),width='stretch')
            st.caption('This graph shows recorded concentration history for the same selected station and period.')
with tabs[2]:
    st.subheader('Pollutant information')
    st.write('See recorded pollutant concentrations for the selected station. These values are separate from the AQI forecast and are not a medical diagnosis.')
    pollutant_day = st.date_input('Selected pollutant date',
                                  min_value=pd.Timestamp('2024-01-01').date(),max_value=pd.Timestamp('2025-12-31').date(),key='pollutant_date',on_change=sync_pollutant_date)
    pollutant_year = pollutant_day.year
    pollutant_hour = hour
    pollutant_data = load_pollutants(pollutant_year)
    source_station = source_station_name(station, pollutant_data['Station Name'].dropna().unique()) if not pollutant_data.empty else None
    if source_station:
        timestamp = pd.Timestamp(pollutant_day) + pd.Timedelta(hours=pollutant_hour)
        records = pollutant_data[(pollutant_data['Station Name'] == source_station) &
                                 (pd.to_datetime(pollutant_data['Timestamp']).dt.tz_localize(None) == timestamp)]
        # Match by the stable pollutant name, avoiding a dependency on how the
        # release encodes the micro and cubic-metre unit symbols.
        pollutant_labels = {
            'PM2.5': 'PM2.5', 'PM10': 'PM10', 'NO2': 'Nitrogen dioxide',
            'Ozone': 'Ozone', 'SO2': 'Sulphur dioxide', 'CO': 'Carbon monoxide',
            'Benzene': 'Benzene'
        }
        value_columns = {
            next((column for column in pollutant_data.columns if column.split(' ')[0] == source_name), None): label
            for source_name, label in pollutant_labels.items()
        }
        value_columns.pop(None, None)
        if records.empty:
            st.info('No recorded value is available for this station and selected time.')
        else:
            row = records.iloc[0]
            values = [{'Pollutant':label,'Recorded concentration':row.get(column)} for column,label in value_columns.items() if pd.notna(row.get(column))]
            if values:
                st.dataframe(pd.DataFrame(values),hide_index=True,width='stretch')
                st.subheader('What these readings may mean')
                st.caption('Colour compares this reading with the same station’s 2025 readings. It shows whether the value is lower, usual, or higher for this station; it is not a medical limit or diagnosis.')
                hazard_text = {
                    'PM2.5': 'Fine particles can irritate the airways and can be more concerning for people with lung or heart conditions.',
                    'PM10': 'Coarser particles can irritate the throat and airways.',
                    'Nitrogen dioxide': 'Can irritate the airways, especially for people with asthma.',
                    'Ozone': 'Can cause throat or chest discomfort during elevated conditions.',
                    'Sulphur dioxide': 'Can irritate the bronchial airways.',
                    'Carbon monoxide': 'Can reduce oxygen delivery and can be more concerning for people with heart conditions.',
                    'Benzene': 'Benzene is a recognised carcinogenic hazard. A short-term reading does not estimate an individual cancer risk.'
                }
                reference = load_pollutants(2025)
                reference_station = source_station_name(station, reference['Station Name'].dropna().unique()) if not reference.empty else None
                for item in values:
                    recorded = pd.to_numeric(pd.Series([item['Recorded concentration']]), errors='coerce').iloc[0]
                    source_column = next((column for column, label in value_columns.items() if label == item['Pollutant']), None)
                    comparison = pd.Series(dtype=float)
                    if reference_station and source_column:
                        comparison = pd.to_numeric(reference.loc[reference['Station Name'] == reference_station, source_column], errors='coerce').dropna()
                    percentile = (comparison <= recorded).mean() * 100 if pd.notna(recorded) and not comparison.empty else None
                    label = f"{item['Pollutant']} · {recorded:g}" if pd.notna(recorded) else item['Pollutant']
                    message = hazard_text[item['Pollutant']]
                    if percentile is None:
                        st.info(f'{label}: {message}')
                    elif percentile >= 90:
                        st.error(f'{label} · higher for this station ({percentile:.0f}th percentile). {message}')
                    elif percentile >= 50:
                        st.warning(f'{label} · usual to higher for this station ({percentile:.0f}th percentile). {message}')
                    else:
                        st.success(f'{label} · lower for this station ({percentile:.0f}th percentile). {message}')
            else:
                st.info('The source record exists, but no selected pollutant values are available at this time.')
    else:
        st.info('No matching 2024–2025 source station was found for this selected station.')
    st.caption('Source: CPCB-derived 2024–2025 station concentration releases, downloaded from the project source record. Times are displayed exactly as supplied by that release. Values are recorded observations, not forecasts.')
    st.link_button('Open the source release page','https://github.com/Vonter/india-cpcb-aqi/releases')
    if pollutant_year in [2024, 2025]:
        st.subheader('Predicted concentrations for the next 24 hours')
        predicted = concentration_forecasts(station, pd.Timestamp(pollutant_day) + pd.Timedelta(hours=pollutant_hour))
        if predicted.empty:
            st.info('A forecast needs 73 continuous recorded hours for every pollutant. This station or time does not have enough complete history.')
        else:
            st.dataframe(concentration_table(predicted),hide_index=True,width='stretch')
            scores=pd.read_csv(ROOT/'experiments/results/concentrations_2017_2025/metrics.csv')
            split = 'validation_2024' if pollutant_year == 2024 else 'test_2025'
            score_view=scores[(scores['split']==split) & (scores['horizon'].isin([1,6,12,24]))][['pollutant','horizon','mae','r2']]
            st.subheader(f'{pollutant_year} forecast accuracy')
            st.dataframe(score_view.rename(columns={'pollutant':'Pollutant','horizon':'Hours ahead','mae':'Average error','r2':'R² quality score'}),hide_index=True,width='stretch')
            period_label = '2024 validation' if pollutant_year == 2024 else 'untouched 2025 test'
            st.caption(f'R² is a model-quality score, not a pollutant percentage. Higher is better; it describes how closely predictions followed observed changes in the {period_label}.')
    st.markdown('**Optional personal precautions**')
    age = st.selectbox('Age group',['Not shared','Under 18','18 to 64','65 or older'])
    lung = st.selectbox('Has a clinician previously told you about asthma, COPD, or another long-term lung condition?',['Not shared','No','Yes'])
    heart = st.selectbox('Has a clinician previously told you about a heart condition?',['Not shared','No','Yes'])
    outdoors = st.selectbox('Will you spend more than one hour outdoors or do strenuous activity during this period?',['Not shared','No','Yes'])
    sensitive = lung == 'Yes' or heart == 'Yes' or age in ['Under 18','65 or older'] or outdoors == 'Yes'
    st.caption('Answers stay in this browser session and do not change the pollution forecast.')
    if sensitive:
        st.warning('High pollution can be more concerning based on the information you selected. During Poor, Very Poor or Severe air quality, consider reducing prolonged outdoor exertion and follow your clinician’s existing advice.')
    else:
        st.caption('Choose the optional answers above for a general precaution message. This project does not diagnose illness or predict a medical outcome.')
with tabs[3]:
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
with tabs[4]:
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
with tabs[5]:
    st.markdown((ROOT/'docs/methodology_guide.md').read_text(encoding='utf-8'))


