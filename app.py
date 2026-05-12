import streamlit as st
import pandas as pd

st.set_page_config(page_title="美多芭分流医院查询看板", layout="centered")

@st.cache_data
def load_data():
    file_path = "3.31美多芭地图覆盖情况 (2).xlsx - 美多芭地图覆盖.csv"
    
    # 自动识别中文字符编码，防止乱码
    try:
        df = pd.read_csv(file_path, encoding='gbk')
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding='gb18030')
        except:
            df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 清除列名里可能不小心打出的空格
    df.columns = [str(col).strip() for col in df.columns]
    
    # 把可能存在的合并空白单元格填满
    if '城市' in df.columns:
        df['城市'] = df['城市'].ffill()
    if '就诊机构名称' in df.columns:
        df['就诊机构名称'] = df['就诊机构名称'].ffill()
        
    return df

try:
    df = load_data()
    
    st.title("🏥 美多芭分流医院查询看板")
    st.markdown("当就诊医院没有美多芭时，查询周边可开药的替代机构。")

    # 1. 城市筛选
    city_list = df['城市'].dropna().unique().tolist()
    selected_city = st.selectbox("1. 请选择城市", city_list)

    if selected_city:
        # 2. 医院筛选（列名已更新为"就诊机构名称"）
        hospitals_in_city = df[df['城市'] == selected_city]['就诊机构名称'].dropna().unique().tolist()
        selected_hospital = st.selectbox("2. 请选择就诊机构", hospitals_in_city)
        
        if selected_hospital:
            # 过滤出选中的城市和医院
            filtered_df = df[(df['城市'] == selected_city) & (df['就诊机构名称'] == selected_hospital)]
            
            # 筛选出可以开药的周边机构（兼容"是"或者"已覆盖"）
            available_df = filtered_df[filtered_df['院边机构本月是否可开'].astype(str).str.contains("是|已覆盖", na=False)]
            
            st.divider()
            st.subheader(f"📍 【{selected_hospital}】 建议分流的周边机构：")
            
            if not available_df.empty:
                # 只展示需要看的两列
                st.dataframe(
                    available_df[['院边机构名称', '院边机构本月是否可开']].reset_index(drop=True), 
                    use_container_width=True
                )
            else:
                st.warning("⚠️ 该机构周边暂无可开美多芭的分流机构。")

except Exception as e:
    st.error(f"❌ 运行遇到一点小问题：{e}")
    st.info("请检查表格的名字是不是依然叫原名，并且和 app.py 放在同一个文件夹哦。")
