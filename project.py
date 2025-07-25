import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import schedule as sch
import requests as req
import nsepython as nse

class Tracking_NSE_Indices:
    def __init__(self, indices, nse_indices):
        self.indices = {
            "NIFTY 50": "^NSEI",
            "NIFTY NEXT 50": "^NSMIDCP",
            "NIFTY 100": "^CNX100",
            "NIFTY 200": "^CNX200",
            "NIFTY 500": "^CNX500",
            "NIFTY MIDCAP 50": "^NSEMDCP50",
            "NIFTY MIDCAP 100": "^CNXMID",
            "NIFTY BANK": "^NSEBANK",
            "NIFTY IT": "^CNXIT",
            "NIFTY FMCG": "^CNXFMCG",
            "NIFTY AUTO": "^CNXAUTO",
            "NIFTY FINANCIAL SERVICES": "^CNXFIN",
            "NIFTY MEDIA": "^CNXMEDIA",
            "NIFTY PHARMA": "^CNXPHARMA",
            "NIFTY METAL": "^CNXMETAL",
            "NIFTY REALTY": "^CNXREALTY",
            "NIFTY SMALLCAP 100": "^CNXSC",
            "NIFTY ENERGY": "^CNXENERGY",
            "NIFTY INFRASTRUCTURE": "^CNXINFRA",
            "NIFTY PSE": "^CNXPSE",
            "NIFTY COMMODITIES": "^CNXCMDT",
            "NIFTY CONSUMPTION": "^CNXCONSUM",
            "NIFTY SERV SECTOR": "CNXSERVICE",
            "NIFTY DIV OPS 50": "^CNXDIVOP",
        }
        
        #backup with nsepython
        self.nse_indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "NIFTYNEXT50", "MIDCPNIFTY",]
        self.data={}
        self.messages_for_log=[]

    def log_information(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"{timestamp} : INFORMATION -> {message}"
        self.messages_for_log.append(entry)
        print(entry)
    
    def log_error(self, error_message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"{timestamp} : ERROR -> {error_message}"
        self.messages_for_log.append(entry)
        print(entry)
    
    def get_data_yfin(self, ticker, symbol):
        try:
            ticker = yf.Ticker(symbol)
            h1d = ticker.history(period="1d", interval="1m")
            h5d = ticker.history(period="5d")
            if h1d.empty or h5d.empty:
                self.log_error(f"Data for {ticker} is empty.")
                return None
            # if not h1d.index[-1].date() == datetime.now().date():
            #     self.log_error(f"Data for {ticker} is not updated for today.")
            #     return None
            if not h1d.empty:
                data = h1d.iloc[-1]
                current_price = float(data['Close'])
                current_time = h1d.index[-1]
                day_open = float(h1d.iloc[0]['Open'])
            else:
                present_data = h5d.iloc[-1]
                current_price = float(present_data['Close'])
                current_time = h5d.index[-1]
                day_open = float(present_data['Open'])

            if len(h5d)>=2:
                prev_close = float(h5d.iloc[-2]['Close'])
            else:
                prev_close = current_price
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0

            try:
                information = ticker.info
                m_cap = information.get('marketCap', 0)
                cur = information.get('currency', 'INR')
            except:
                m_cap = "N/A"
                cur = "Indian National Rupee (INR)"
            return {
                "Index Name": ticker,
                "Symbol": symbol,
                "Current Price": current_price,
                "Open Price": day_open,
                "Previous Close": prev_close,
            }
        
        except Exception as exp:
            self.log_error(f"Error fetching data for {ticker}: {exp}")
            return None
        
    def backup_fetching_through_nse(self, ticker):
        try:
            if ticker in self.nse_indices:
                data = nse.get_index_quote(ticker)
                if not data:
                    self.log_error(f"No data found for {ticker} using nsepython.")
                    return None
                current_price = float(data['lastPrice'])
                day_open = float(data['dayHigh'])
                prev_close = float(data['previousClose'])
                return {
                    "Index Name": ticker,
                    "Symbol": ticker,
                    "Current Price": current_price,
                    "Open Price": day_open,
                    "Previous Close": prev_close,
                }
        except Exception as exp:
            self.log_error(f"Error fetching data for {ticker} using nsepython: {exp}")
            return None
        
    def summary(self):
        if not data:
            print("No data is available due to possible error.")
        
        print("Summary of NSE Indices:")
        for index, ticker in self.indices.items():
            data = self.get_data_yfin(ticker, ticker)
            if data:
                print(f"{index} ({data['Symbol']}): Current Price: {data['Current Price']}, Open Price: {data['Open Price']}, Previous Close: {data['Previous Close']}")
            else:
                backup_data = self.backup_fetching_through_nse(index)
                if backup_data:
                    print(f"{index} ({backup_data['Symbol']}): Current Price: {backup_data['Current Price']}, Open Price: {backup_data['Open Price']}, Previous Close: {backup_data['Previous Close']}")
                else:
                    print(f"No data available for {index}.")

    def saving_summary(self, data, filename = None):
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            f_name = f"nse_indices_summary_{timestamp}.txt"
        try:
            F1 = open(filename, "w")
            F1.write("Summary of NSE Indices:\n")
            for index, ticker in self.indices.items():
                if ticker in data:
                    d = data[ticker]
                    F1.write(f"{index} ({d['Symbol']}): Current Price: {d['Current Price']}, Open Price: {d['Open Price']}, Previous Close: {d['Previous Close']}\n")
                else:
                    backup_data = self.backup_fetching_through_nse(index)
                    if backup_data:
                        F1.write(f"{index} ({backup_data['Symbol']}): Current Price: {backup_data['Current Price']}, Open Price: {backup_data['Open Price']}, Previous Close: {backup_data['Previous Close']}\n")
                    else:
                        F1.write(f"No data available for {index}.\n")
            F1.close()
            self.log_information(f"Summary saved to {filename}")
        except Exception as exp:
            self.log_error(f"Error saving summary to {filename}: {exp}")
            return None
        
    def update(self):
        self.log_information("Updating NSE indices data...")
        print("Update in progress...")
        start = time.tim()
        self.current_data = {}
        for index, ticker in self.indices.items():
            data = self.get_data_yfin(ticker, ticker)
            if data:
                self.current_data[ticker] = data
            else:
                backup_data = self.backup_fetching_through_nse(index)
                if backup_data:
                    self.current_data[ticker] = backup_data
                else:
                    self.log_error(f"No data available for {index}.")
        end = time.time()
        self.log_information(f"Update completed in {end - start:.2f} seconds.")
        return self.current_data
    
    def schedular(self):
        sch.every().day.at("09:15", "Asia/Kolkata").do(self.update)
        sch.every().day.at("15:30", "Asia/Kolkata").do(self.update)

    def run_scheduler(self):
        self.log_information("Starting scheduler for NSE indices updates...")
        try:
            while True:
                sch.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.log_information("Scheduler stopped by user.")    

def main():
    record_1 =  {"NIFTY 50": "^NSEI",
            "NIFTY NEXT 50": "^NSMIDCP",
            "NIFTY 100": "^CNX100",
            "NIFTY 200": "^CNX200",
            "NIFTY 500": "^CNX500",
            "NIFTY MIDCAP 50": "^NSEMDCP50",
            "NIFTY MIDCAP 100": "^CNXMID",
            "NIFTY BANK": "^NSEBANK",
            "NIFTY IT": "^CNXIT",
            "NIFTY FMCG": "^CNXFMCG",
            "NIFTY AUTO": "^CNXAUTO",
            "NIFTY FINANCIAL SERVICES": "^CNXFIN",
            "NIFTY MEDIA": "^CNXMEDIA",
            "NIFTY PHARMA": "^CNXPHARMA",
            "NIFTY METAL": "^CNXMETAL",
            "NIFTY REALTY": "^CNXREALTY",
            "NIFTY SMALLCAP 100": "^CNXSC",
            "NIFTY ENERGY": "^CNXENERGY",
            "NIFTY INFRASTRUCTURE": "^CNXINFRA",
            "NIFTY PSE": "^CNXPSE",
            "NIFTY COMMODITIES": "^CNXCMDT",
            "NIFTY CONSUMPTION": "^CNXCONSUM",
            "NIFTY SERV SECTOR": "CNXSERVICE",
            "NIFTY DIV OPS 50": "^CNXDIVOP"}
    
    record_2 = ["NIFTY", "BANKNIFTY", "FINNIFTY", "NIFTYNEXT50", "MIDCPNIFTY"]
    tracker = Tracking_NSE_Indices(record_1, record_2)
    tracker.schedular()
    tracker.run_scheduler()
    print("Please Select one of the following options: \n1.Immediate Update\n2.Scheduled Update\n3.Summary of NSE Indices\n4.Save Summary to File\n5.Exit")
    while True:
        choice = int(input("Enter your choice (1-5): "))
        if choice == 1:
            tracker.update()
        elif choice == 2:
            tracker.run_scheduler()
        elif choice == 3:
            tracker.summary()
        elif choice == 4:
            filename = input("Enter filename to save summary (or press Enter for default): ")
            tracker.saving_summary(tracker.current_data, filename if filename else None)
        elif choice == 5:
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()

