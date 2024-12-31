老師好

我希望能夠做一個針對股票分析的agent
能夠針對不同場景來做分析提供不同的回覆，例如使用者想做長線的股票又或者是想要即時資訊來判斷哪支股票適合當沖

透過分析即時的新聞，判斷市場情緒，歷史股價的概率分析，提供使用者及時最新的資訊

在更深的畫就會希望能開發一個有交易策略，並且可以自動下單操作的ai

我DINO 和 Kingsley 一組~

股票agent
curl -X POST "http://127.0.0.1:8000/stock" \
-H "Content-Type: application/json" \
-d '{"stock_symbol": "AAPL"}'