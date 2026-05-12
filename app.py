import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib # 日本語表示のためにインポート
import matplotlib.patches as patches

# データフレームの初期化
# 既存のデータがない状態で始める場合は、空のデータフレームを作成します。
# カラム名を定義しておくことで、新しいデータ追加時にエラーを防ぎます。
if 'df' not in locals():
    df = pd.DataFrame(columns=['pitch_x', 'pitch_y', 'ball_direction', 'exit_velocity', 'pitch_type'])

print("データフレームが準備できました。")



# 新しい打席データを入力するための「入力専用の表」
new_entries = [
    # ここに新しいデータを追加してください (例を参考に記述してください)
    {
        'pitch_x': -0.8,   # 例: 左低め
        'pitch_y': 2.0,    # 例: 低め
        'ball_direction': 'Left', # 例: 左方向
        'exit_velocity': 108, # 例: 108 mph
        'pitch_type': 'Fastball' # 例: ストレート
    },
    {
        'pitch_x': 0.1,    # 例: 真ん中高め
        'pitch_y': 3.1,    # 例: 高め
        'ball_direction': 'Center', # 例: センター方向
        'exit_velocity': 98,  # 例: 98 mph
        'pitch_type': 'Curveball' # 例: カーブ
    }
    # 必要に応じて、さらにデータを追加
]

# 新しいデータをDataFrameに変換
new_df_to_add = pd.DataFrame(new_entries)

# 既存のデータフレームに新しいデータを追加
df = pd.concat([df, new_df_to_add], ignore_index=True)

print("新しいデータが追加されました。データフレームの最後の5行:")
display(df.tail())



display(df)





# 投球位置の散布図
plt.figure(figsize=(8, 10)) # 縦長の長方形に変更
sns.scatterplot(x='pitch_x', y='pitch_y', hue='pitch_type', data=df, s=100, alpha=0.7) # hueを球種に変更
plt.title('投球位置と球種') # タイトルも変更
plt.xlabel('投球の左右位置 (捕手視点など)')
plt.ylabel('投球の高さ位置 (地面からなど)')
plt.grid(True)

# x軸とy軸の範囲を調整してボール球も含む
plt.xlim(-2.0, 2.0)
plt.ylim(-4.0, 4.0) # ストライクゾーンとボール球の範囲を考慮してy軸の表示範囲を調整

# ストライクゾーンを太線で囲む (x: -1.5から1.5, y: -2.5から2.5)
strike_zone = patches.Rectangle((-1.5, -2.5), 3.0, 5.0, linewidth=3, edgecolor='red', facecolor='none', linestyle='--')
plt.gca().add_patch(strike_zone)

# x軸とy軸を等間隔にする
plt.gca().set_aspect('equal', adjustable='box')

plt.show()



# 打球方向ごとの打球速度の箱ひげ図
plt.figure(figsize=(8, 6))
sns.boxplot(x='ball_direction', y='exit_velocity', data=df)
plt.title('打球方向ごとの打球速度')
plt.xlabel('打球方向')
plt.ylabel('打球速度 (mph)')
plt.grid(axis='y')
plt.show()




 打球方向ごとの投球位置と球種の散布図をファセットグリッドで表示
# col='ball_direction' で打球方向ごとにグラフを分割します。
# hue='pitch_type' で球種ごとに色分けします。

g = sns.relplot(x='pitch_x', y='pitch_y', hue='pitch_type', col='ball_direction', data=df, kind='scatter', s=100, alpha=0.7, col_wrap=3, height=5, aspect=0.8)

g.set_axis_labels('投球の左右位置', '投球の高さ位置')
g.set_titles(col_template='打球方向: {col_name}')
g.fig.suptitle('打球方向ごとの投球位置と球種', y=1.02) # 全体タイトル

# 各サブプロットにストライクゾーンを追加
for ax in g.axes.flat:
    strike_zone = patches.Rectangle((-1.5, -2.5), 3.0, 5.0, linewidth=1, edgecolor='red', facecolor='none', linestyle='--')
    ax.add_patch(strike_zone)
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(-4.0, 4.0)
    ax.set_aspect('equal', adjustable='box')

plt.tight_layout() # レイアウトの調整
plt.show()
