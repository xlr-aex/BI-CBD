# -*- coding: utf-8 -*-
"""
BI Pro CBD Shops v2.5.2
Date:  Mai 2025
Contributeur améliorations : vous
"""

# 📦 Imports & Config
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import listparser
import xml.parsers.expat
import feedparser
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import re
import io
import importlib

# 👷 Détection moteur Excel
try:
    importlib.import_module("xlsxwriter")
    EXCEL_ENGINE = "xlsxwriter"
except ModuleNotFoundError:
    try:
        importlib.import_module("openpyxl")
        EXCEL_ENGINE = "openpyxl"
    except ModuleNotFoundError:
        EXCEL_ENGINE = None

st.set_page_config(page_title="BI Pro CBD Shops – v2.5.2", layout="wide", page_icon="🌿")

# 🔖 Constantes
CATEGORIES_KEYWORDS = {
    "Huiles CBD/Dérivés": ["huile", "oil", "gouttes", "drops", "cbd oil", "full spectrum", "broad spectrum", "teinture", "tincture"],
    "Fleurs & Résines CBD/Dérivés": ["fleur", "flower", "bud", "trim", "résine", "resin", "hash", "pollen", "jelly", "moonrock", "icerock", "shit"],
    "Vapes CBD/Dérivés": ["vape", "e-liquide", "e-liquid", "cartridge", "puff", "pod", "vaporisateur", "distillat vape"],
    "Comestibles CBD/Dérivés": ["gummy", "gummies", "bonbon", "edible", "chocolat", "thé", "infusion", "boisson", "miel", "pastille"],
    "Cosmétiques CBD": ["crème", "baume", "serum", "cosmétique", "balm", "cream", "lotion", "savon", "shampoing"],
    "Autres Molécules (HHC, THCP, etc.)": ["HHC", "THCP", "H4CBD", "VMAC", "POKE"],
    "Concentrés & Extraits": ["concentré", "extrait", "distillate", "isolate", "wax", "shatter", "crumble", "cristaux"],
    "Accessoires": ["grinder", "feuille", "pipe", "bang", "accessoire"],
}
DEFAULT_DATE_RANGE_DAYS = 90
CANNABINOIDS_TARGET = ["CBD", "CBG", "CBN", "THC", "THCV"]
RATE_COLUMNS = [f"{c}_rate" for c in CANNABINOIDS_TARGET]
TLD_TO_COUNTRY = {
    'fr':'France','de':'Germany','uk':'United Kingdom','es':'Spain','it':'Italy','nl':'Netherlands',
    'be':'Belgium','ch':'Switzerland','at':'Austria','pt':'Portugal','dk':'Denmark','se':'Sweden',
    'no':'Norway','fi':'Finland','ie':'Ireland','pl':'Poland','cz':'Czech Republic','hu':'Hungary',
    'ro':'Romania','bg':'Bulgaria','gr':'Greece','hr':'Croatia','si':'Slovenia','sk':'Slovakia',
    'lt':'Lithuania','lv':'Latvia','ee':'Estonia','cy':'Cyprus','mt':'Malta','lu':'Luxembourg',
    'is':'Iceland','li':'Liechtenstein','mc':'Monaco','ad':'Andorra','sm':'San Marino','va':'Vatican City',
}

# 🔧 Utils
def normalize_product_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    s = name.lower()
    s = re.sub(r"\b(\d+)\s*(g|gr|ml|mg)\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\b\d+%?\b", "", s)
    return s.strip()

def extract_cannabinoid_rates(product_name: str) -> dict:
    rates = {c: None for c in CANNABINOIDS_TARGET}
    text = product_name or ""
    spans = []
    # THC < X%
    m = re.search(r"THC\s*<\s*(\d+(?:[.,]\d+)?)\s*%", text, re.IGNORECASE)
    if m:
        try:
            rates["THC"] = float(m.group(1).replace(",", "."))
            spans.append(m.span())
        except: pass
    # spécifiques
    for canna in CANNABINOIDS_TARGET:
        if rates[canna] is not None: continue
        pats = []
        if canna=="THCV":
            pats = [rf"(?:THCV|THV2)\s*:?\s*(\d+(?:[.,]\d+)?)\s*%", rf"(\d+(?:[.,]\d+)?)\s*%\s*(?:de\s*)?(?:THCV|THV2)\b"]
        else:
            pats = [rf"{re.escape(canna)}\s*:?\s*(\d+(?:[.,]\d+)?)\s*%", rf"(\d+(?:[.,]\d+)?)\s*%\s*(?:de\s*)?{re.escape(canna)}\b"]
        for pat in pats:
            for mm in re.finditer(pat, text, re.IGNORECASE):
                sp = mm.span()
                if any(max(a,sp[0])<min(b,sp[1]) for a,b in spans): continue
                try:
                    val = float(mm.group(1).replace(",", "."))
                    rates[canna]=val
                    spans.append(sp)
                    break
                except: pass
            if rates[canna] is not None: break
    # fallback CBD
    if rates["CBD"] is None:
        for mm in re.finditer(r"(\d+(?:[.,]\d+)?)\s*%", text, re.IGNORECASE):
            sp=mm.span()
            if any(max(a,sp[0])<min(b,sp[1]) for a,b in spans): continue
            try:
                rates["CBD"]=float(mm.group(1).replace(",", "."))
                break
            except: pass
    return rates

def categorize(name_norm: str) -> str:
    if not name_norm: return "Produits Non Catégorisés"
    if any(k.lower() in name_norm for k in CATEGORIES_KEYWORDS["Autres Molécules (HHC, THCP, etc.)"]):
        return "Autres Molécules (HHC, THCP, etc.)"
    for cat,kws in CATEGORIES_KEYWORDS.items():
        if cat.startswith("Autres Molécules"): continue
        if any(k.lower() in name_norm for k in kws): return cat
    return "Produits Non Catégorisés"

@st.cache_data(show_spinner=False)
def get_domain(url: str) -> str:
    if not url: return "inconnu"
    if not url.startswith(("http://","https://")): url="http://"+url
    try:
        dn=urlparse(url).netloc.lower()
        return dn[4:] if dn.startswith("www.") else dn
    except: return "inconnu"

@st.cache_data(show_spinner=False)
def parse_opml(opml_bytes: bytes):
    try:
        return listparser.parse(opml_bytes.decode("utf-8")).feeds
    except Exception as e:
        st.error(f"Erreur parsing OPML : {e}")
        return []

def safe_datetime_parse(t):
    try:
        return datetime(*t[:6]) if t else None
    except: return None

def fetch_feed_data(feed_url: str, shop_domain: str):
    products=[]
    try:
        pf=feedparser.parse(
            feed_url,
            request_headers={"User-Agent":"Mozilla/5.0 (compatible; CBDAnalyticsBot/1.0; +http://example.com/bot)"}
        )
        # ignore any bozo feeds silently
        if pf.bozo:
            return []
        for entry in pf.entries:
            name=entry.get("title","N/A")
            rates=extract_cannabinoid_rates(name)
            norm=normalize_product_name(name)
            cat=categorize(norm)
            pub=None
            for a in ("published_parsed","updated_parsed"):
                pub=safe_datetime_parse(getattr(entry,a,None))
                if pub: break
            rec={'boutique_domain':shop_domain,
                 'product_name':name,
                 'product_name_normalized':norm,
                 'product_category':cat,
                 'product_link':entry.get("link","#"),
                 'product_published_date':pub,
                 'feed_url':feed_url}
            for c,v in rates.items(): rec[f"{c}_rate"]=v
            products.append(rec)
    except Exception as e:
        st.warning(f"Erreur extraction flux {feed_url} : {e}")
    return products

@st.cache_data(ttl=1800, show_spinner=False)
def load_all_feeds_data(feeds_list):
    all_products=[]  
    prog=st.empty().progress(0, text="Chargement des flux RSS...")
    total=len(feeds_list)
    if total==0:
        prog.empty()
        return pd.DataFrame()
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_feed = {}
        for feed in feeds_list:
            feed_url = getattr(feed, "xmlUrl", None) or getattr(feed, "url")
            shop_dom = get_domain(getattr(feed, "htmlUrl", None) or feed_url)
            future = executor.submit(fetch_feed_data, feed_url, shop_dom)
            future_to_feed[future] = (feed_url, shop_dom)

        for i, future in enumerate(as_completed(future_to_feed), 1):
            feed_url, shop_dom = future_to_feed[future]
            try:
                prods = future.result()
                all_products.extend(prods)
            except Exception as exc:
                st.warning(f"Erreur threading flux {feed_url} : {exc}")
            prog.progress(i/total, text=f"[{i}/{total}] {shop_dom}")

    prog.empty()

    # — DEBUG : bilan des flux —
    status=[]
    for feed in feeds_list:
        url=getattr(feed,"xmlUrl",None) or getattr(feed,"url")
        cnt=sum(1 for p in all_products if p.get("feed_url")==url)
        status.append({"feed_url":url,"produits":cnt,"statut":"OK" if cnt>0 else "KO"})
    st.subheader("🔍 Bilan des Flux RSS")
    st.dataframe(pd.DataFrame(status))
    # — fin debug —

    df=pd.DataFrame(all_products)
    if not df.empty:
        df["product_published_date"]=pd.to_datetime(df["product_published_date"],errors="coerce")
        for c in CANNABINOIDS_TARGET:
            col=f"{c}_rate"
            if col not in df: df[col]=pd.NA
            else: df[col]=pd.to_numeric(df[col],errors="coerce")
    return df

# 🎛️ UI – Import & Filtres
st.title("🚀 BI Pro – Shops CBD (v2.5.2)")
st.sidebar.header("Configuration & Filtres")

uploaded=st.sidebar.file_uploader("1️⃣ OPML des flux RSS",type=["opml","xml"])
min_date=date(2000,1,1)
today=date.today()

if 'date_range_selection' not in st.session_state:
    st.session_state.date_range_selection=(today-timedelta(days=DEFAULT_DATE_RANGE_DAYS),today)
start_date,end_date=st.sidebar.date_input(
    "2️⃣ Période d'analyse",
    value=st.session_state.date_range_selection,
    min_value=min_date,max_value=today
)
st.session_state.date_range_selection=(start_date,end_date)

gran=st.sidebar.radio("3️⃣ Granularité",("Jour","Semaine","Mois"),index=1,horizontal=True)
freq_map={"Jour":"D","Semaine":"W-Mon","Mois":"MS"}
time_freq=freq_map[gran]

if not uploaded:
    st.info("👈 Importez un OPML pour commencer")
    st.stop()

feeds=parse_opml(uploaded.getvalue())
if not feeds:
    st.error("OPML invalide ou vide.")
    st.stop()

if 'current_opml_name' not in st.session_state or st.session_state.current_opml_name!=uploaded.name:
    st.session_state.current_opml_name=uploaded.name
    if 'df_master_data' in st.session_state: del st.session_state['df_master_data']

if st.sidebar.button("🚀 Analyser les flux"):
    with st.spinner("Analyse en cours…"):
        dfm=load_all_feeds_data(feeds)
        if dfm.empty:
            st.warning("Aucun produit récupéré. Vérifiez vos flux/période.")
        else:
            st.session_state['df_master_data']=dfm
            st.sidebar.success(f"Terminée : {len(dfm)} produits")

if 'df_master_data' not in st.session_state or st.session_state.df_master_data.empty:
    st.warning("Pas de données à afficher.")
    st.stop()

df_master=st.session_state.df_master_data
if not pd.api.types.is_datetime64_any_dtype(df_master['product_published_date']):
    df_master['product_published_date']=pd.to_datetime(df_master['product_published_date'],errors="coerce")

dt_start=datetime.combine(start_date,datetime.min.time())
dt_end=datetime.combine(end_date,datetime.max.time())
mask=(df_master['product_published_date']>=dt_start)&(df_master['product_published_date']<=dt_end)
df_date=df_master.loc[mask].copy()
if df_date.empty:
    st.warning("Aucun produit sur la période.")
    st.stop()

all_shops=sorted(df_date['boutique_domain'].unique())
all_cats=sorted(df_date['product_category'].unique())

with st.sidebar.expander("🔍 Filtres avancés",True):
    filt_shops=st.multiselect("Boutiques",options=all_shops,default=all_shops)
    filt_cats=st.multiselect("Catégories",options=all_cats,default=all_cats)

df_final=df_date[df_date['boutique_domain'].isin(filt_shops)&df_date['product_category'].isin(filt_cats)]
if df_final.empty:
    st.warning("Filtres trop restrictifs.")
    st.stop()

tabs=["Vue générale","Comparaison","Analyse par Boutique","Explorateur de Données"]
if 'tab' not in st.session_state: st.session_state.tab=0
st.sidebar.markdown("---")
active=st.sidebar.radio("Vue :",tabs,index=st.session_state.tab,key="t")
st.session_state.tab=tabs.index(active)

if active=="Vue générale":
    st.header("📊 Vue générale")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Articles",len(df_final))
    c2.metric("Boutiques actives",df_final['boutique_domain'].nunique())
    c3.metric("Catégories actives",df_final['product_category'].nunique())
    jours=(end_date-start_date).days+1
    c4.metric("Période",f"{jours} jours")
    st.markdown("---")
    # Top boutiques
    l1,l2=st.columns(2)
    with l1:
        ts=df_final['boutique_domain'].value_counts().nlargest(15).reset_index()
        ts.columns=['Boutique','Nb']
        fig1=px.bar(ts,x='Boutique',y='Nb',color='Boutique',height=400)
        st.plotly_chart(fig1,use_container_width=True)
    with l2:
        tc=df_final['product_category'].value_counts().reset_index()
        tc.columns=['Catégorie','Nb']
        fig2=px.pie(tc,names='Catégorie',values='Nb',hole=0.35,height=400,
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2,use_container_width=True)
    st.markdown("---")
    # Time series
    a1,a2=st.columns(2)
    with a1:
        ts2=df_final.set_index('product_published_date').resample(time_freq).size().reset_index(name='Nb')
        fig3=px.line(ts2,x='product_published_date',y='Nb',markers=True,height=350)
        st.plotly_chart(fig3,use_container_width=True)
    with a2:
        hm=pd.crosstab(df_final['product_category'],df_final['boutique_domain'])
        if not hm.empty:
            fig4=go.Figure(data=go.Heatmap(z=hm.values,x=hm.columns,y=hm.index,colorscale='Viridis'))
            fig4.update_layout(height=400)
            st.plotly_chart(fig4,use_container_width=True)
    st.markdown("---")
    # Cannabinoïdes
    cols=[col for col in RATE_COLUMNS if col in df_final.columns]
    if cols:
        avg=df_final.groupby('boutique_domain')[cols].mean().reset_index()
        melt=avg.melt(id_vars='boutique_domain',value_vars=cols,
                      var_name='Canna',value_name='Taux')
        melt['Canna']=melt['Canna'].str.replace('_rate','')
        fig5=px.bar(melt,x='boutique_domain',y='Taux',color='Canna',barmode='group',height=400)
        st.plotly_chart(fig5,use_container_width=True)
    # Carte & tableau unique
    df_final['tld']=df_final['boutique_domain'].apply(lambda d:d.split('.')[-1].lower())
    df_final['country']=df_final['tld'].map(TLD_TO_COUNTRY).fillna('International')
    dc=df_final[['boutique_domain','country']].drop_duplicates()
    cc=dc['country'].value_counts().reset_index().rename(columns={'index':'Pays','country':'Nb_boutiques'})
    cm=cc[cc['Pays']!='International']
    st.subheader("🌍 Carte des Boutiques par Pays")
    if not cm.empty:
        fig6=px.choropleth(cm,locations='Pays',locationmode='country names',
                           color='Nb_boutiques',hover_name='Pays',
                           color_continuous_scale='YlOrRd',
                           range_color=(0,cm['Nb_boutiques'].max()))
        fig6.update_layout(height=500)
        st.plotly_chart(fig6,use_container_width=True)
    st.subheader("📋 Détail Boutiques par Pays")
    bc=dc.groupby('country')['boutique_domain'].apply(list).reset_index().rename(columns={'country':'Pays','boutique_domain':'Boutiques'})
    bc['Nombre de Boutiques']=bc['Boutiques'].apply(len)
    bc['Boutiques']=bc['Boutiques'].apply(lambda lst: ", ".join(f"<a href='https://{d}' target='_blank'>{d}</a>" for d in lst))
    st.markdown(bc[['Pays','Nombre de Boutiques','Boutiques']].to_html(escape=False,index=False),unsafe_allow_html=True)

elif active=="Comparaison":
    st.header("⚖️ Comparaison")
    shops_sel=st.multiselect("Boutiques",all_shops,default=all_shops[:2])
    if not shops_sel:
        st.warning("Sélectionnez au moins une boutique."); st.stop()
    dfc=df_final[df_final['boutique_domain'].isin(shops_sel)]
    c1,c2=st.columns(2)
    with c1:
        d1=dfc.groupby(['boutique_domain',pd.Grouper(key='product_published_date',freq=time_freq)])\
             .size().reset_index(name='Nb')
        d1.columns=['Boutique','Date','Nb']
        fig=px.bar(d1,x='Date',y='Nb',color='Boutique',barmode='group',height=400)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        d2=dfc.groupby(['product_category',pd.Grouper(key='product_published_date',freq=time_freq)])\
             .size().reset_index(name='Nb')
        d2.columns=['Catégorie','Date','Nb']
        fig=px.bar(d2,x='Date',y='Nb',color='Catégorie',barmode='group',height=400)
        st.plotly_chart(fig,use_container_width=True)

elif active=="Analyse par Boutique":
    st.header("🛍️ Analyse Boutique")
    shop=st.selectbox("Boutique",all_shops)
    dfb=df_final[df_final['boutique_domain']==shop]
    if dfb.empty: st.warning("Pas de données pour cette boutique."); st.stop()
    c1,c2=st.columns(2)
    with c1:
        st.metric("Articles",len(dfb))
        st.metric("Taux moyen CBD",f"{dfb['CBD_rate'].mean():.2f}%")
    with c2:
        st.metric("Catégories",dfb['product_category'].nunique())
        st.metric("Taux moyen THC",f"{dfb['THC_rate'].mean():.2f}%")
    st.markdown("---")
    # Pie catégories
    pc=dfb['product_category'].value_counts().reset_index(); pc.columns=['Catégorie','Nb']
    fig=px.pie(pc,names='Catégorie',values='Nb',hole=0.3,height=350)
    st.plotly_chart(fig,use_container_width=True)
    # Timeseries
    ts=dfb.set_index('product_published_date').resample(time_freq).size().reset_index(name='Nb')
    fig=px.line(ts,x='product_published_date',y='Nb',markers=True,height=350)
    st.plotly_chart(fig,use_container_width=True)
    # Top 20
    cols=['product_published_date','product_name','product_category']+[c for c in RATE_COLUMNS if c in dfb.columns]
    df20=dfb[cols].sort_values('product_published_date',ascending=False).head(20)
    df20=df20.rename(columns={'product_published_date':'Date','product_name':'Nom','product_category':'Catégorie'})
    st.dataframe(df20.set_index('Date'))

else:  # Explorateur de Données
    st.header("🔍 Explorateur")
    cols=['boutique_domain','product_name','product_category','product_published_date','product_link']\
         +[c for c in RATE_COLUMNS if c in df_final.columns]
    de=df_final[cols].rename(columns={
        'boutique_domain':'Boutique','product_name':'Nom','product_category':'Catégorie',
        'product_published_date':'Date','product_link':'Lien'
    }).set_index('Date').sort_index(ascending=False)
    st.dataframe(de,use_container_width=True)
    if EXCEL_ENGINE:
        buf=io.BytesIO()
        with pd.ExcelWriter(buf,engine=EXCEL_ENGINE) as w: de.reset_index().to_excel(w,index=False,sheet_name="Données")
        st.download_button("📥 Télécharger Excel",buf.getvalue(),
                           file_name=f"bi_pro_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("Installez xlsxwriter ou openpyxl pour l’export Excel.")

# Pied de page
st.sidebar.markdown("---")
st.sidebar.info("BI Pro CBD Shops v2.5.2")