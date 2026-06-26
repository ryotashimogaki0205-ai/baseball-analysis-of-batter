import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import math
import os
from datetime import datetime
from supabase import create_client

# --- Supabase 設定 ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hpzpkdyvjlvpfzbeddax.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_Fr-2qh2FJ6h2eKoP6m55RA_sHLYKzRo")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", None)
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "batting_data")

APP_COLUMNS = [
    'チーム名', '選手名', '打席ID', 'コース', '球種', '捕球位置',
    '打球角度', '投手の投げ手', 'カウント', '結果', '入力日時'
]
DB_TO_APP_COLS = {
    'team_name': 'チーム名',
    'player_name': '選手名',
    'plate_id': '打席ID',
    'course': 'コース',
    'pitch_type': '球種',
    'catch_position': '捕球位置',
    'batted_ball_angle': '打球角度',
    'pitcher_hand': '投手の投げ手',
    'count': 'カウント',
    'result': '結果',
    'input_datetime': '入力日時'
}
APP_TO_DB_COLS = {v: k for k, v in DB_TO_APP_COLS.items()}


def get_empty_dataframe():
    return pd.DataFrame(columns=APP_COLUMNS)


def get_supabase_config():
    url = SUPABASE_URL
    key = SUPABASE_KEY
    if hasattr(st, 'secrets') and st.secrets is not None:
        supabase = st.secrets.get('supabase') if isinstance(st.secrets, dict) else None
        if supabase:
            url = supabase.get('url', url)
            key = supabase.get('key', key)
            if 'service_key' in supabase:
                key = supabase.get('service_key', key)
    url = os.getenv('SUPABASE_URL', url)
    key = os.getenv('SUPABASE_KEY', key)
    service_key = os.getenv('SUPABASE_SERVICE_KEY', SUPABASE_SERVICE_KEY)
    if service_key:
        key = service_key
    return url, key


def parse_missing_column_message(message):
    if not isinstance(message, str):
        return None
    import re

    patterns = [
        r"Could not find the '([^']+)' column",
        r"column .*?\.([a-zA-Z0-9_]+) does not exist",
        r"column \"?([a-zA-Z0-9_]+)\"? of .+? does not exist",
    ]
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1)
    return None


def get_supported_db_columns():
    return list(DB_TO_APP_COLS.keys())


def filter_record_columns(record, allowed_columns):
    return {k: v for k, v in record.items() if k in allowed_columns}


def get_supabase_client():
    url, key = get_supabase_config()
    if not url or not key:
        st.warning("SupabaseのURLまたはキーが設定されていません。SUPABASE_URL / SUPABASE_KEY を確認してください。")
        return None
    return create_client(url, key)


def load_data_from_supabase():
    """Supabaseからデータを読み込む"""
    try:
        client = get_supabase_client()
        if client is None:
            return get_empty_dataframe()

        response = client.table(SUPABASE_TABLE).select("*").order('input_datetime', desc=False).execute()
        if getattr(response, 'error', None):
            error_message = getattr(response.error, 'message', response.error)
            if 'PGRST205' in str(error_message) or 'Could not find the table' in str(error_message):
                st.warning(
                    f"Supabaseテーブルが見つかりません: {SUPABASE_TABLE}。"
                    "Supabase管理画面でテーブル名とAPIキーを確認してください。"
                )
            raise Exception(error_message)

        data = response.data or []
        if len(data) == 0:
            return get_empty_dataframe()

        df = pd.DataFrame(data)
        df.rename(columns=DB_TO_APP_COLS, inplace=True)
        if '入力日時' in df.columns:
            df['入力日時'] = pd.to_datetime(df['入力日時'], errors='coerce')
        return df
    except Exception as e:
        st.warning(f"Supabaseデータ読み込みエラー: {str(e)}")
        return get_empty_dataframe()


def save_record_to_supabase(record):
    """Supabaseに新規レコードを保存する（サービスキーを使用して RLS をバイパス）"""
    try:
        url, _ = get_supabase_config()
        service_key = os.getenv("SUPABASE_SERVICE_KEY", SUPABASE_SERVICE_KEY)
        
        # RLS をバイパスするためにサービスキーでクライアントを作成
        if service_key:
            client = create_client(url, service_key)
        else:
            st.warning("SUPABASE_SERVICE_KEY が設定されていません。データを保存できません。")
            return False

        db_record = {APP_TO_DB_COLS[k]: v for k, v in record.items() if k in APP_TO_DB_COLS}
        response = client.table(SUPABASE_TABLE).insert([db_record]).execute()

        if getattr(response, 'error', None):
            error_message = getattr(response.error, 'message', response.error)
            if 'PGRST205' in str(error_message) or 'Could not find the table' in str(error_message):
                st.warning(
                    f"Supabaseテーブルが見つかりません: {SUPABASE_TABLE}。"
                    "Supabase管理画面でテーブル名とAPIキーを確認してください。"
                )
            elif '42501' in str(error_message) or 'row-level security' in str(error_message):
                st.warning(
                    "Row Level Security (RLS) ポリシーエラー。"
                    "SUPABASE_SERVICE_KEY が正しく設定されているか確認してください。"
                )
            raise Exception(error_message)

        return True
    except Exception as e:
        st.warning(f"Supabaseデータ保存エラー: {str(e)}")
        return False


def create_baseball_field():
    fig = go.Figure()

    # 実測距離の比率に基づくスケール
    draw_scale = 2.0
    base_distance = 27.0 * draw_scale
    second_distance = 40.0 * draw_scale
    foul_pole_distance = 100.0 * draw_scale
    center_fence_distance = 123.0 * draw_scale

    first_x = base_distance / math.sqrt(2)
    first_y = base_distance / math.sqrt(2)
    third_x = -first_x
    third_y = first_y
    second_x = 0.0
    second_y = second_distance

    # 外野フェンス（左右のポールとセンターの距離を反映した曲線）
    theta = [math.radians(angle) for angle in range(45, 136, 2)]
    x_fence = []
    y_fence = []
    for t in theta:
        ratio = math.sin((t - math.radians(45)) / math.radians(90) * math.pi)
        r = foul_pole_distance + (center_fence_distance - foul_pole_distance) * ratio
        x_fence.append(r * math.cos(t))
        y_fence.append(r * math.sin(t))
    fig.add_trace(go.Scatter(x=x_fence, y=y_fence, mode='lines', line=dict(color='white', width=4), showlegend=False))

    # ファールライン
    fp = foul_pole_distance / math.sqrt(2)
    fig.add_trace(go.Scatter(x=[0, fp], y=[0, fp], mode='lines', line=dict(color='white', width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=[0, -fp], y=[0, fp], mode='lines', line=dict(color='white', width=2), showlegend=False))

    # 内野の土（薄茶色）
    dirt_x = [0, first_x, second_x, third_x, 0]
    dirt_y = [0, first_y, second_y, third_y, 0]
    fig.add_trace(go.Scatter(x=dirt_x, y=dirt_y, fill='toself', fillcolor='#D2B48C', line=dict(color='white', width=2), showlegend=False))

    # 内野ベースライン
    fig.add_trace(go.Scatter(x=[0, first_x, second_x, third_x, 0], y=[0, first_y, second_y, third_y, 0], mode='lines', line=dict(color='white', width=2), showlegend=False))

    # ホームベース（ファールラインに沿う正方形）
    base_side = 4.0 * draw_scale
    v1 = (base_side / math.sqrt(2), base_side / math.sqrt(2))
    v2 = (-base_side / math.sqrt(2), base_side / math.sqrt(2))
    home_base_x = [0, v1[0], v1[0] + v2[0], v2[0], 0]
    home_base_y = [0, v1[1], v1[1] + v2[1], v2[1], 0]
    fig.add_trace(go.Scatter(x=home_base_x, y=home_base_y, fill='toself', fillcolor='white', line=dict(color='white', width=2), showlegend=False))

    # 1塁（正方形）
    f1_v1 = (-base_side / math.sqrt(2), -base_side / math.sqrt(2))
    f1_v2 = (-base_side / math.sqrt(2), base_side / math.sqrt(2))
    f1_x = [first_x, first_x + f1_v1[0], first_x + f1_v1[0] + f1_v2[0], first_x + f1_v2[0], first_x]
    f1_y = [first_y, first_y + f1_v1[1], first_y + f1_v1[1] + f1_v2[1], first_y + f1_v2[1], first_y]
    fig.add_trace(go.Scatter(x=f1_x, y=f1_y, fill='toself', fillcolor='white', line=dict(color='white', width=2), showlegend=False))

    # 3塁（正方形）
    f3_v1 = (base_side / math.sqrt(2), -base_side / math.sqrt(2))
    f3_v2 = (base_side / math.sqrt(2), base_side / math.sqrt(2))
    f3_x = [third_x, third_x + f3_v1[0], third_x + f3_v1[0] + f3_v2[0], third_x + f3_v2[0], third_x]
    f3_y = [third_y, third_y + f3_v1[1], third_y + f3_v1[1] + f3_v2[1], third_y + f3_v2[1], third_y]
    fig.add_trace(go.Scatter(x=f3_x, y=f3_y, fill='toself', fillcolor='white', line=dict(color='white', width=2), showlegend=False))

    # 2塁（正方形）
    s_v = base_side / math.sqrt(2)
    s_x = [second_x, second_x + s_v, second_x, second_x - s_v, second_x]
    s_y = [second_y - s_v, second_y, second_y + s_v, second_y, second_y - s_v]
    fig.add_trace(go.Scatter(x=s_x, y=s_y, fill='toself', fillcolor='white', line=dict(color='white', width=2), showlegend=False))

    # ピッチャーズマウンド
    mound_distance = 18.44 * draw_scale
    fig.add_shape(type='circle', xref='x', yref='y', x0=-4 * draw_scale, y0=mound_distance - 4 * draw_scale, x1=4 * draw_scale, y1=mound_distance + 4 * draw_scale, fillcolor='#D2B48C', line=dict(color='white', width=2))

    # ファウルポール
    pole_height = 25 * draw_scale
    fig.add_trace(go.Scatter(x=[fp, fp], y=[fp, fp + pole_height], mode='lines', line=dict(color='yellow', width=8), showlegend=False))
    fig.add_trace(go.Scatter(x=[-fp, -fp], y=[fp, fp + pole_height], mode='lines', line=dict(color='yellow', width=8), showlegend=False))

    # 背景全体をクリック可能にするための密集したグリッド状マーカー
    grid_x = []
    grid_y = []
    for x in range(-210, 211, 10):  # 10単位ごとの密集グリッド
        for y in range(-85, 336, 10):
            grid_x.append(x)
            grid_y.append(y)
    
    fig.add_trace(go.Scatter(
        x=grid_x,
        y=grid_y,
        mode='markers',
        marker=dict(size=3, opacity=0.1, color='rgba(255,255,255,0.1)'),
        hoverinfo='skip',
        showlegend=False,
        name='grid'
    ))

    fig.update_layout(
        xaxis=dict(
            range=[-210, 210],
            autorange=False,
            showgrid=False,
            zeroline=False,
            constrain='domain'
        ),
        yaxis=dict(
            range=[-85, 335],
            autorange=False,
            showgrid=False,
            zeroline=False,
            scaleanchor='x',
            scaleratio=1
        ),
        plot_bgcolor='green',
        paper_bgcolor='green',
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=False,
        title='野球フィールド（クリックして捕球位置を選択）',
        height=720,
        width=720,
        autosize=False,
        clickmode='event'
    )

    return fig


def create_baseball_field_with_catches(catch_positions_str_list):
    """捕球位置を赤いドットで表示する球場図を作成"""
    fig = create_baseball_field()
    
    # 捕球位置データをパース
    catch_x_list = []
    catch_y_list = []
    hover_texts = []
    
    # 座標をカウント
    position_count = {}
    
    for pos_str in catch_positions_str_list:
        try:
            # "(x, y)" 形式の文字列をパース
            pos_str = pos_str.strip('()')
            x_str, y_str = pos_str.split(',')
            x = float(x_str.strip())
            y = float(y_str.strip())
            catch_x_list.append(x)
            catch_y_list.append(y)
            
            # 同じ座標の回数をカウント
            key = (round(x, 2), round(y, 2))
            if key not in position_count:
                position_count[key] = 0
            position_count[key] += 1
            
            hover_texts.append(f"({x:.2f}, {y:.2f})")
        except (ValueError, AttributeError):
            # パースに失敗した場合はスキップ
            continue
    
    # 赤いドットを追加
    if catch_x_list:
        fig.add_trace(go.Scatter(
            x=catch_x_list,
            y=catch_y_list,
            mode='markers',
            marker=dict(
                color='red',
                size=10,
                opacity=0.8,
                line=dict(color='darkred', width=1)
            ),
            text=hover_texts,
            hovertemplate='<b>捕球位置</b><br>%{text}<extra></extra>',
            name='捕球位置',
            showlegend=True
        ))
    
    return fig

st.set_page_config(layout="wide", page_title="野球打球分析ツール")

st.title("⚾ 野球打球分析ツール")
st.write("投球と打球のデータを入力し、分析結果を確認できます。")

# --- セッションステートの初期化 --- #
if 'all_batting_data' not in st.session_state:
    # Supabaseからデータを読み込む
    st.session_state.all_batting_data = load_data_from_supabase()

if 'selected_pitch_location' not in st.session_state:
    st.session_state.selected_pitch_location = None

if 'selected_catch_position' not in st.session_state:
    st.session_state.selected_catch_position = None

# --- 球種分類のヘルパー --- #
PITCH_TYPE_CATEGORY = {
    'ストレート': '直球',
    'シンカー': '直球',
    'カーブ': '変化球',
    'スライダー': '変化球',
    'フォーク': '変化球',
    'チェンジアップ': '変化球',
    'カットボール': '変化球',
    'その他': '変化球'
}

def add_pitch_type_category(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['球種区分'] = df['球種'].map(PITCH_TYPE_CATEGORY).fillna('変化球')
    return df

# --- サイドバーでのデータ表示 --- #
st.sidebar.header("現在の記録")
if not st.session_state.all_batting_data.empty:
    st.sidebar.dataframe(st.session_state.all_batting_data)
else:
    st.sidebar.write("まだデータがありません。")

# --- データ入力セクション --- #
st.header("打席データ入力")

# チーム名と選手名の入力
team_name = st.text_input("チーム名を入力してください", "")
player_name = st.text_input("選手名を入力してください", "")

if 'last_team_name' not in st.session_state:
    st.session_state.last_team_name = ''
if 'last_player_name' not in st.session_state:
    st.session_state.last_player_name = ''

if team_name and player_name and (
    team_name != st.session_state.last_team_name or player_name != st.session_state.last_player_name
):
    st.session_state.selected_pitch_location = None
    st.session_state.selected_catch_position = None
    st.session_state.last_team_name = team_name
    st.session_state.last_player_name = player_name

if team_name and player_name:
    st.subheader(f"{team_name} - {player_name} の打席記録")

    # 投球データを上部に集約
    st.markdown("#### 投球データ")
    st.markdown("**投球コース（捕手目線の9分割ストライクゾーン）**")

    strike_zone = [
        ['高め内角', '高め真ん中', '高め外角'],
        ['真ん中内角', '真ん中', '真ん中外角'],
        ['低め内角', '低め真ん中', '低め外角']
    ]

    for row in strike_zone:
        cols = st.columns(3)
        for label, column in zip(row, cols):
            if column.button(label, key=f"pitch_{label}"):
                st.session_state.selected_pitch_location = label

    st.markdown("**ボール球（ゾーン外）**")
    ball_zone_row = ['ボール球（内角）', 'ボール球（真ん中）', 'ボール球（外角）']
    cols = st.columns(3)
    for label, column in zip(ball_zone_row, cols):
        if column.button(label, key=f"pitch_{label}"):
            st.session_state.selected_pitch_location = label

    pitch_location = st.session_state.selected_pitch_location
    if pitch_location:
        st.success(f"選択中の投球コース: {pitch_location}")
    else:
        st.info("捕手目線のストライクゾーンからコースを選択してください。")

    # 投球データの選択肢を1行に配置
    col_pitch1, col_pitch2, col_pitch3 = st.columns(3)
    
    with col_pitch1:
        pitch_type_options = ['ストレート', 'カーブ', 'スライダー', 'フォーク', 'チェンジアップ', 'シンカー', 'カットボール', 'その他']
        pitch_type = st.selectbox("球種を選択", pitch_type_options, key='pitch_type')
    
    with col_pitch2:
        pitcher_hand = st.radio("投手の投げ手", ['右', '左'], key='pitcher_hand', horizontal=True)

    with col_pitch3:
        count_options = ['0-0', '0-1', '0-2', '1-0', '1-1', '1-2', '2-0', '2-1', '2-2', '3-0', '3-1', '3-2']
        count = st.selectbox("カウント", count_options, key='count')

    # 空行で視認性向上
    st.markdown("---")

    # 打球データセクション：球場図を全幅で大きく表示
    st.markdown("#### 打球データ")
    st.markdown("**捕球位置（球場模式図で指定）**")

    # X座標とY座標のスライダー入力
    col_slider1, col_slider2 = st.columns(2)
    
    with col_slider1:
        catch_x = st.slider("X座標（左=-210, 右=210）", min_value=-210, max_value=210, value=0, step=1, key='catch_x')
    
    with col_slider2:
        catch_y = st.slider("Y座標（下=-85, 上=335）", min_value=-85, max_value=335, value=0, step=1, key='catch_y')
    
    # 座標の保存
    st.session_state.selected_catch_position = f"({catch_x:.2f}, {catch_y:.2f})"
    
    # プレビュー用：入力座標を表示する球場図
    fig_preview = create_baseball_field_with_catches([st.session_state.selected_catch_position])
    st.plotly_chart(fig_preview, use_container_width=True, key='preview_field')
    
    st.success(f"現在の捕球位置: {st.session_state.selected_catch_position}")

    # 打球角度と結果を3カラムで配置
    col_result1, col_result2, col_result3 = st.columns(3)
    
    with col_result1:
        # 打球角度をカテゴリ選択 → 内部的に数値に変換
        batted_ball_angle_options = {'ゴロ（0°）': 0.0, 'ライナー（20°）': 20.0, 'フライ（45°）': 45.0, '邪飛（60°）': 60.0, 'その他（30°）': 30.0}
        batted_ball_angle_label = st.selectbox("打球角度を選択", list(batted_ball_angle_options.keys()), key='bb_angle')
        batted_ball_angle = batted_ball_angle_options[batted_ball_angle_label]

    with col_result2:
        result_options = ['凡退', '単打', '二塁打', '三塁打', '本塁打', '四球', '死球', '犠打', '犠飛', '三振', '出塁']
        result = st.selectbox("結果を選択", result_options, key='result')
    
    with col_result3:
        pass  # スペース確保

    # データ保存ボタン
    if st.button("打席データを記録"):
        catch_position = st.session_state.selected_catch_position
        if not pitch_location or not catch_position:
            st.warning("投球コースと捕球位置を両方選択してください。")
        else:
            new_data = {
                'チーム名': team_name,
                '選手名': player_name,
                '打席ID': pd.Timestamp.now().strftime("%Y%m%d%H%M%S%f"), # ユニークな打席ID
                'コース': pitch_location,
                '球種': pitch_type,
                '捕球位置': catch_position,
                '打球角度': batted_ball_angle,
                '投手の投げ手': pitcher_hand,
                'カウント': count,
                '結果': result,
                '入力日時': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if save_record_to_supabase(new_data):
                st.session_state.all_batting_data = pd.concat(
                    [st.session_state.all_batting_data, pd.DataFrame([new_data])],
                    ignore_index=True
                )
                st.success("打席データがSupabaseに記録されました！")
            else:
                st.warning("Supabaseへの保存に失敗しました。接続情報とテーブル設定を確認してください。")

            st.session_state.selected_pitch_location = None
            st.session_state.selected_catch_position = None

    # --- 投球と打球のリンク表示（簡易版） --- #
    st.markdown("### 記録された打席データ（リンク表示）")
    if not st.session_state.all_batting_data.empty:
        # 現在の選手に絞って表示
        current_player_data = st.session_state.all_batting_data[
            (st.session_state.all_batting_data['チーム名'] == team_name) &
            (st.session_state.all_batting_data['選手名'] == player_name)
        ].sort_values(by='入力日時', ascending=False)
        
        if not current_player_data.empty:
            st.write("**最新の打席データ:**")
            latest_record = current_player_data.iloc[0]
            st.info(
                f"コース: {latest_record['コース']}、球種: {latest_record['球種']}、"
                f"打球角度: {latest_record['打球角度']}、捕球位置: {latest_record['捕球位置']}、"
                f"結果: {latest_record['結果']}"
            )
            st.markdown("---")
            st.write("**これまでの打席データ:**")
            st.dataframe(current_player_data[['入力日時', 'コース', '球種', '打球角度', '捕球位置', '結果']])

            st.markdown("### この選手の集計")
            result_summary = current_player_data.groupby('結果').size().rename('件数').reset_index()
            st.dataframe(result_summary)

            st.markdown("#### 投球コース別件数")
            course_summary = current_player_data.groupby('コース').size().rename('件数').reset_index()
            st.dataframe(course_summary)

            st.markdown("#### 捕球位置分布（球場模式図）")
            # 捕球位置を赤いドットで表示
            catch_positions = current_player_data['捕球位置'].tolist()
            fig_with_catches = create_baseball_field_with_catches(catch_positions)
            st.plotly_chart(fig_with_catches, use_container_width=True)

            st.markdown("#### 捕球位置別件数")
            catch_summary = current_player_data.groupby('捕球位置').size().rename('件数').reset_index()
            st.dataframe(catch_summary)

            current_player_data = add_pitch_type_category(current_player_data)

            st.markdown("#### 右投手・左投手別 捕球位置割合")
            hand_summary = current_player_data.groupby(['投手の投げ手', '捕球位置']).size().rename('件数').reset_index()
            hand_summary['割合'] = hand_summary.groupby('投手の投げ手')['件数'].transform(lambda x: (x / x.sum() * 100).round(1))
            hand_ratio_pivot = hand_summary.pivot(index='投手の投げ手', columns='捕球位置', values='割合').fillna(0).astype(float)
            st.dataframe(hand_ratio_pivot)
            st.bar_chart(hand_ratio_pivot)

            st.markdown("#### 直球・変化球別 捕球位置割合")
            type_summary = current_player_data.groupby(['球種区分', '捕球位置']).size().rename('件数').reset_index()
            type_summary['割合'] = type_summary.groupby('球種区分')['件数'].transform(lambda x: (x / x.sum() * 100).round(1))
            type_ratio_pivot = type_summary.pivot(index='球種区分', columns='捕球位置', values='割合').fillna(0).astype(float)
            st.dataframe(type_ratio_pivot)
            st.bar_chart(type_ratio_pivot)
        else:
            st.write("この選手にはまだデータがありません。")

        st.markdown("### 打者別集計")
        batter_summary = st.session_state.all_batting_data.groupby(['チーム名', '選手名']).agg(
            打席数=('打席ID', 'count'),
            最新入力日時=('入力日時', 'max')
        ).reset_index()
        st.dataframe(batter_summary.sort_values(['チーム名', '選手名']))
    else:
        st.write("まだ打席データが記録されていません。")


    # --- データの保存と管理 --- #
    st.markdown("### データの保存と管理")
    st.success("✅ データは自動的にSupabaseに保存されています。")
    st.markdown(f"📊 Supabase テーブル: `{SUPABASE_TABLE}` に保存されます。")
    
    # データリロードボタン
    if st.button("Supabaseからデータを再読み込み"):
        st.session_state.all_batting_data = load_data_from_supabase()
        st.success("Supabaseのデータを再読み込みしました！")
        st.rerun()

else:
    st.info("チーム名と選手名を入力して、打席記録を開始してください。")