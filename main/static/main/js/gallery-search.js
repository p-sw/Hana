class GalleryBlock {
    constructor() {
        this.galleries_per_page = 25;
        this.query = decodeURIComponent(window.location.search);
        if (/[?&]page=\d+/.test(this.query)) {
            this.page = parseInt(/[?&]page=(\d+)/.exec(this.query)[1], 10);
        } else {
            this.page = 1;
        }

        this.query_tags = /[?&]tags=([+\-a-z_:]+)/.exec(this.query)[1];

        this.start_byte = (this.page - 1) * this.galleries_per_page * 4;
        this.end_byte = this.start_byte + this.galleries_per_page * 4 - 1;

        this.sort(this.query_tags);
    }

    sort(tags) {
        this.positives = Array.prototype.map.call([...tags.matchAll(/\+([a-z:_]+)/g)], (m) => m[1].replace("_", " "));
        this.negatives = Array.prototype.map.call([...tags.matchAll(/-([a-z:_]+)/g)], (m) => m[1].replace("_", " "));
    }

    load(area, tag, language) {
        return fetch(`/api/get-nozomi?area=${area}&tag=${tag}&language=${language}&comp_prefix=n`, {
            method: 'GET',
        }).then(response => {
            return response.arrayBuffer();
        }).then(buffer => {
            const view = new DataView(buffer);
            const results = [];
            for (let i = 0; i < view.byteLength/4; i++) {
                results.push(view.getInt32(i*4, false));
            }
            return results;
        })
    }

    process_tag(tag) {
        const sides = tag.split(":");
        const ns = sides[0];
        let tag_r = sides[1];

        let area = ns;
        let language = "all";
        if (ns === "female" || ns === "male") {
            area = "tag";
            tag_r = tag;
        } else if (ns === "language") {
            area = undefined;
            language = tag_r;
            tag_r = 'index';
        }

        return this.load(area, tag_r, language)
    }

    process_executor() {
        new Promise((resolve, reject) => {
            // first result
            if (!this.positives.length) {
                this.load(undefined, 'index', 'all').then((data) => {
                    resolve(data);
                })
            } else {
                this.process_tag(this.positives.shift()).then((data) => {
                    resolve(data);
                })
            }
        }).then((data) => {
            // positive
            if (this.positives.length) {
                console.log(data);
                return Promise.all(this.positives.map(tag => {
                    return new Promise((resolve, reject) => {
                        this.process_tag(tag).then(new_results => {
                            const new_results_set = new Set(new_results);
                            resolve(data.filter(galleryid => new_results_set.has(galleryid)));
                        });
                    });
                }));
            } else {
                return data;
            }

        }).then((data) => {
            // negative
            if (this.negatives.length) {
                return Promise.all(this.negatives.map(tag => {
                    return new Promise((resolve, reject) => {
                        this.process_tag(tag).then(new_results => {
                            const new_results_set = new Set(new_results);
                            resolve(data.filter(galleryid => !new_results_set.has(galleryid)));
                        });
                    });
                }));
            } else {
                return data;
            }
        }).then((data) => {
            // final
            document.querySelector("#result-length").innerText = data.length;
            this.put(data.slice((this.page - 1) * this.galleries_per_page, this.page * this.galleries_per_page));
        })
    }

    put(items) {
        for (let id of items) {
            fetch(`/api/get-galleryblock?id=${id}`, {
                method: 'GET',
            }).then(response => {
                return response.text();
            }).then(html => {
                let block = document.createElement("article");
                block.classList.add("gallery-block");
                block.innerHTML = html;
                return block;
            }).then(block => { // post-processing
                // remove 2nd, 3rd image
                block.querySelector("div a.lillie div[class*=-img-cont] div[class*=-img2]").remove()
                block.querySelector("div a.lillie div[class*=-img-cont] div[class*=-img-back]").remove()
                // set thumbnail
                let src = block.querySelector("div a.lillie div[class*=-img-cont] picture source");
                let img = block.querySelector("div a.lillie div[class*=-img-cont] picture img");
                if (src) {
                    src.src = "/api/get-image?url=https:"+/(\S+)\s1x/.exec(src.dataset.srcset)[1];
                    src.classList.add("lazyload");
                }
                if (img) {
                    img.src = "/api/get-image?url=https:"+img.dataset.src;
                    img.classList.add("lazyload");
                }
                // add column container, add all thing except image container
                let col = document.createElement("div");
                col.classList.add("col");
                col.appendChild(block.querySelector("div h1.lillie"));
                col.appendChild(block.querySelector("div div.artist-list"))
                col.appendChild(block.querySelector("div div[class*=-content]"))
                block.querySelector("div").appendChild(col);
                block.setAttribute("style", `order: ${items.indexOf(id)};`);
                document.getElementById("gallery").appendChild(block);
            })
        }
    }
}

const search = new GalleryBlock();
search.process_executor();