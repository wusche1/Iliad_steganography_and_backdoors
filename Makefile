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

site-data:
	uv run python scripts/tools/build_site.py $(LECTURES)

site:
	rm -rf _site && mkdir -p _site/bib
	cp -r site/. _site/
	for l in $(LECTURES); do cp lectures/$$l/output/main.pdf _site/$$l.pdf; done
	rsync -a --include='*/' --include='*_fulltext.md' --include='figures/*.png' --exclude='*' --prune-empty-dirs bib/ _site/bib/

serve: site
	cd _site && python3 -m http.server 8000

.PHONY: slides clean update-links test site-data site serve $(LECTURES)
