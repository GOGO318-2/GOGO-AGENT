import { useState, useEffect } from 'react';
import './index.css';

function App() {
  const [stockCode, setStockCode] = useState('');
  const [stockData, setStockData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  // 获取推荐股票
  useEffect(() => {
    fetch('https://gogo-agent-backend.railway.app/recommend')
      .then(res => res.json())
      .then(data => setRecommendations(data))
      .catch(err => console.error(err));
  }, []);

  // 查询股票
  const handleQuery = () => {
    fetch('https://gogo-agent-backend.railway.app/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stock_code: stockCode })
    })
      .then(res => res.json())
      .then(data => setStockData(data))
      .catch(err => console.error(err));
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">GOGO-AGENT 美股推荐系统</h1>

      {/* 查询区域 */}
      <div className="mb-6">
        <input
          type="text"
          value={stockCode}
          onChange={e => setStockCode(e.target.value)}
          placeholder="输入股票代码（如 AAPL）"
          className="border p-2 mr-2 rounded"
        />
        <button
          onClick={handleQuery}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          查询
        </button>
      </div>

      {/* 查询结果 */}
      {stockData && (
        <div className="border p-4 mb-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold">查询结果: {stockData.code}</h2>
          <p>当前价格: ${stockData.current_price?.toFixed(2)}</p>
          <p>20日均线: ${stockData.sma20?.toFixed(2)}</p>
          <p>RSI: {stockData.rsi?.toFixed(2)}</p>
          <p>MACD: {stockData.macd?.toFixed(2)}</p>
          <p>操作建议: {stockData.rsi < 30 ? '买入（超卖）' : stockData.rsi > 70 ? '卖出（超买）' : '持有'}</p>
        </div>
      )}

      {/* 推荐列表 */}
      <h2 className="text-xl font-semibold mb-4">推荐股票</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map(stock => (
          <div key={stock.code} className="border p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold">{stock.name} ({stock.code})</h3>
            <p>当前价格: ${stock.current_price?.toFixed(2)}</p>
            {stock.buy_price && <p>买入价格: ${stock.buy_price?.toFixed(2)}</p>}
            {stock.sell_price && <p>卖出价格: ${stock.sell_price?.toFixed(2)}</p>}
            {stock.shares > 0 && <p>建议股数: {stock.shares}</p>}
            <p>推荐理由: {stock.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;