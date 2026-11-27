# Catastrophe Theory Animations — Build System
#
# Usage:
#   make all        — render all scenes at medium quality
#   make preview    — render all at low quality (fast iteration)
#   make hd         — render all at 1080p60
#   make <scene>    — render one scene (e.g., make fold)
#   make clean      — remove rendered media
#
# Individual scenes:
#   make fold cusp relu horizon figure1
#
# Pace control (for reading time):
#   PACE=0.7 make all   — expert pace (faster text)
#   PACE=1.5 make all   — presentation pace (slower text)

MANIM = manim
SCENE_DIR = scenes
MEDIA_DIR = media

# Quality flags
QL = -ql    # 480p15 — fast preview
QM = -qm    # 720p30 — medium (default)
QH = -qh    # 1080p60 — high quality
QK = -qk    # 2160p60 — 4K

# Default quality
Q = $(QM)

# All scenes and their classes:
SCENES = \
	fold \
	cusp \
	cusp_trace \
	relu \
	figure1 \
	horizon \
	earth_fig1 \
	geo_fig1 \
	umap

# Scene file → class mapping:
fold_FILE      = $(SCENE_DIR)/whitney_fold.py
fold_CLASS     = FoldSingularity

cusp_FILE      = $(SCENE_DIR)/whitney_cusp.py
cusp_CLASS     = CuspSingularity

cusp_trace_FILE  = $(SCENE_DIR)/cusp_tracing.py
cusp_trace_CLASS = CuspTracing

relu_FILE      = $(SCENE_DIR)/relu_as_max.py
relu_CLASS     = ReLUAsMax

figure1_FILE   = $(SCENE_DIR)/arnold_figure1.py
figure1_CLASS  = ArnoldFigure1

horizon_FILE   = $(SCENE_DIR)/horizon_max_function.py
horizon_CLASS  = HorizonMaxFunction

earth_fig1_FILE  = $(SCENE_DIR)/earth_figure1.py
earth_fig1_CLASS = EarthArnoldFigure1

geo_fig1_FILE    = $(SCENE_DIR)/geodesic_figure1.py
geo_fig1_CLASS   = GeodesicFigure1

umap_FILE     = $(SCENE_DIR)/umap_projection.py
umap_CLASS    = UMAPProjection

# ─── Targets ──────────────────────────────────────────────

.PHONY: all preview hd 4k clean $(SCENES)

all: $(SCENES)

preview:
	$(MAKE) Q="$(QL)" all

hd:
	$(MAKE) Q="$(QH)" all

4k:
	$(MAKE) Q="$(QK)" all

# Individual scene targets:
$(SCENES):
	$(MANIM) $(Q) $($@_FILE) $($@_CLASS)

# ─── Convenience aliases ─────────────────────────────────

# Render and auto-open (-p flag):
play-%:
	$(MANIM) -p $(QL) $($*_FILE) $($*_CLASS)

# ─── Viewing ──────────────────────────────────────────────

# Open all rendered previews in the default media player:
view_preview:
	@for f in $(MEDIA_DIR)/videos/*/480p15/*.mp4; do \
		echo "Opening: $$f"; \
		xdg-open "$$f" 2>/dev/null & \
	done

view_hd:
	@for f in $(MEDIA_DIR)/videos/*/1080p60/*.mp4; do \
		echo "Opening: $$f"; \
		xdg-open "$$f" 2>/dev/null & \
	done

# View a single scene's latest render:
view-%:
	@find $(MEDIA_DIR)/videos -name "*.mp4" -path "*$**" | sort | tail -1 | xargs xdg-open 2>/dev/null

# ─── Concatenation ────────────────────────────────────────

# Scene order for the concatenated film:
FILM_ORDER = fold figure1 cusp cusp_trace relu horizon

# Build a single mp4 from all scenes (preview quality):
film_preview: preview
	@echo "Concatenating preview scenes into film..."
	@mkdir -p $(MEDIA_DIR)/film
	@rm -f /tmp/manim_concat_list.txt
	@for s in $(FILM_ORDER); do \
		f=$$(find $(MEDIA_DIR)/videos -name "*.mp4" -path "*480p*" -path "*$$($${s}_CLASS)*" | sort | tail -1); \
		if [ -n "$$f" ]; then echo "file '$$f'" >> /tmp/manim_concat_list.txt; echo "  + $$f"; fi; \
	done
	ffmpeg -y -f concat -safe 0 -i /tmp/manim_concat_list.txt -c copy $(MEDIA_DIR)/film/catastrophe_theory_preview.mp4
	@echo "Film: $(MEDIA_DIR)/film/catastrophe_theory_preview.mp4"

# Build a single mp4 from all scenes (HD quality):
film_hd: hd
	@echo "Concatenating HD scenes into film..."
	@mkdir -p $(MEDIA_DIR)/film
	@rm -f /tmp/manim_concat_list.txt
	@for s in $(FILM_ORDER); do \
		f=$$(find $(MEDIA_DIR)/videos -name "*.mp4" -path "*1080p*" -path "*$$($${s}_CLASS)*" | sort | tail -1); \
		if [ -n "$$f" ]; then echo "file '$$f'" >> /tmp/manim_concat_list.txt; echo "  + $$f"; fi; \
	done
	ffmpeg -y -f concat -safe 0 -i /tmp/manim_concat_list.txt -c copy $(MEDIA_DIR)/film/catastrophe_theory_hd.mp4
	@echo "Film: $(MEDIA_DIR)/film/catastrophe_theory_hd.mp4"

# Concatenate from whatever's already rendered (don't re-render):
film:
	@echo "Concatenating best available renders into film..."
	@mkdir -p $(MEDIA_DIR)/film
	@rm -f /tmp/manim_concat_list.txt
	@for s in $(FILM_ORDER); do \
		f=$$(find $(MEDIA_DIR)/videos -name "*.mp4" -path "*$$($${s}_CLASS)*" | sort | tail -1); \
		if [ -n "$$f" ]; then echo "file '$$f'" >> /tmp/manim_concat_list.txt; echo "  + $$f"; fi; \
	done
	ffmpeg -y -f concat -safe 0 -i /tmp/manim_concat_list.txt -c copy $(MEDIA_DIR)/film/catastrophe_theory.mp4
	@echo "Film: $(MEDIA_DIR)/film/catastrophe_theory.mp4"

view_film:
	@f=$$(ls -t $(MEDIA_DIR)/film/*.mp4 2>/dev/null | head -1); \
	if [ -n "$$f" ]; then xdg-open "$$f" 2>/dev/null; \
	else echo "No film yet — run 'make film' first"; fi

# ─── Examples (Python, not manim) ─────────────────────────

earth:
	python3 examples/earth_projection.py

earth_real:
	python3 examples/earth_realistic.py

# ─── Housekeeping ─────────────────────────────────────────

clean:
	rm -rf $(MEDIA_DIR)

# List available scenes:
list:
	@echo "Available scenes:"
	@for s in $(SCENES); do \
		echo "  make $$s      — $${s}_CLASS"; \
	done
	@echo ""
	@echo "Shortcuts:"
	@echo "  make play-fold   — render + open fold"
	@echo "  make preview     — all scenes at 480p (fast)"
	@echo "  make hd          — all scenes at 1080p60"
	@echo "  make 4k          — all scenes at 4K"
