all: 20190226-thalesians-london-seminar.html

20190226/skew_plot.html 20190226/spread_plot.html: market_maker_control.py
	mkdir -p 20190226
	python3 market_maker_control.py

20190226-thalesians-london-seminar.html: OptionsMarketMaking.md 20190226/skew_plot.html 20190226/spread_plot.html
	pandoc -s -t revealjs -V theme=white -V revealjs-url=. --mathjax --toc --toc-depth=1 -o 20190226-thalesians-london-seminar.html OptionsMarketMaking.md
