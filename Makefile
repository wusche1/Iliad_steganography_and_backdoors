TEXBIN = /Library/TeX/texbin
LECTURES = steganography backdoors

slides: $(LECTURES)

$(LECTURES):
	cd lectures/$@ && mkdir -p output && \
	$(TEXBIN)/pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=output main.tex && \
	$(TEXBIN)/biber --output-directory=output main && \
	$(TEXBIN)/pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=output main.tex && \
	$(TEXBIN)/pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=output main.tex

clean:
	rm -rf lectures/*/output

update-links:
	uv run python scripts/tools/update_colab_links.py

test:
	uv run pytest tests/ -v

.PHONY: slides clean update-links test $(LECTURES)
