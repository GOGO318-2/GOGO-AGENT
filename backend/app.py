from flask import Flask, request, jsonify
from flask_cors import CORS
import finnhub
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 部署后改为 Netlify URL

# 初始化 Finnhub 客户端
finnhub_client = finnhub.Client(api_key="d1p1qv9r01qi9vk2517gd1p1qv9r01qi9vk25180")

@app.route('/recommend', methods=['GET'])
def recommend():
    stocks = ['AAPL', 'GOOGL', 'AMZN']
    recommendations = []

    for stock in stocks:
        try:
            # 获取最近 60 天的日线数据
            end_date = int(datetime.now().timestamp())
            start_date = int((datetime.now() - timedelta(days=60)).timestamp())
            data = finnhub_client.stock_candles(stock, 'D', start_date, end_date)
            
            if not data['s'] == 'ok':
                continue

            close = np.array(data['c'], dtype=np.double)
            if len(close) < 20:
                continue

            # 计算技术指标
            sma20 = np.mean(close[-20:])  # 20 日均线
            rsi = finnhub_client.technical_indicator(symbol=stock, resolution='D', from_=start_date, to=end_date, indicator='rsi', indicator_fields={"timeperiod": 14})['rsi'][-1]
            macd = finnhub_client.technical_indicator(symbol=stock, resolution='D', from_=start_date, to=end_date, indicator='macd')['macd'][-1]
            signal = finnhub_client.technical_indicator(symbol=stock, resolution='D', from_=start_date, to=end_date, indicator='macd')['signal'][-1]

            # 当前价格
            current_price = close[-1]

            # 推荐逻辑
            buy_price = current_price if rsi < 30 and current_price > sma20 else None
            sell_price = current_price * 1.15 if rsi > 70 else None
            reason = ""
            if buy_price:
                reason = f"RSI ({rsi:.2f}) 超卖，价格突破 20 日均线 ({sma20:.2f})，MACD ({macd:.2f}) 看涨，建议周一买入，周五卖出"
            elif sell_price:
                reason = f"RSI ({rsi:.2f}) 超买，建议获利了结"

            # 计算股数（目标盈利 $5000）
            shares = int(5000 / (sell_price - buy_price)) if buy_price and sell_price else 0

            recommendations.append({
                'code': stock,
                'name': stock,
                'current_price': current_price,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'shares': shares,
                'reason': reason
            })
        except Exception as e:
            print(f"Error processing {stock}: {e}")
            continue

    return jsonify(recommendations)

@app.route('/query', methods=['POST'])
def query_stock():
    data = request.get_json()
    stock_code = data.get('stock_code')
    try:
        # 获取实时价格
        quote = finnhub_client.quote(stock_code)
        if not quote['c']:
            return jsonify({'error': '无数据'}), 404

        # 获取技术指标
        end_date = int(datetime.now().timestamp())
        start_date = int((datetime.now() - timedelta(days=60)).timestamp())
        sma20 = np.mean(finnhub_client.stock_candles(stock_code, 'D', start_date, end_date)['c'][-20:])
        rsi = finnhub_client.technical_indicator(symbol=stock_code, resolution='D', from_=start_date, to=end_date, indicator='rsi', indicator_fields={"timeperiod": 14})['rsi'][-1]
        macd = finnhub_client.technical_indicator(symbol=stock_code, resolution='D', from_=start_date, to=end_date, indicator='macd')['macd'][-1]
        signal = finnhub_client.technical_indicator(symbol=stock_code, resolution='D', from_=start_date, to=end_date, indicator='macd')['signal'][-1]

        return jsonify({
            'code': stock_code,
            'current_price': quote['c'],
            'sma20': sma20,
            'rsi': rsi,
            'macd': macd,
            'signal': signal
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)