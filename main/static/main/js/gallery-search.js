class PageNavigator {
    constructor(pages) {
        this.max_page = pages

        this.query = decodeURIComponent(window.location.search);
        if (/[?&]page=\d+/.test(this.query)) {
            this.current_page = parseInt(/[?&]page=(\d+)/.exec(this.query)[1], 10);
        } else {
            this.current_page = 1;
        }

        /* configurations */
        this.build_parent = document.querySelector("section#page-navigation")

        this.page_button_per_page = 10;
    }

    build() {
        let page_navigator = document.createElement("nav");
        page_navigator.classList.add("page-navigator");

        let page_min = Math.floor(this.current_page / 10) * 10 + 1;
        let page_max = Math.min(page_min + (this.page_button_per_page - 1), this.max_page);

        let page_prev = document.createElement("a");
        page_prev.classList.add("page-prev");
        page_prev.href = this.build_query(this.current_page - 1);
        page_navigator.appendChild(page_prev);

        for (let i=page_min;i<=page_max;i++) {
            let page_button = document.createElement("a");
            page_button.classList.add("page-button");
            page_button.href = this.build_query(i);
            page_button.innerText = i.toString();
            if (i === this.current_page) {
                page_button.classList.add("current-page");
                page_button.href = '';
            }
            page_navigator.appendChild(page_button);
        }

        let page_next = document.createElement("a");
        page_next.classList.add("page-next");
        page_next.href = this.build_query(this.current_page + 1);
        page_navigator.appendChild(page_next);

        this.build_parent.appendChild(page_navigator);
    }

    build_query(page) {
        if (/[?&]page=\d+/.test(this.query)) {
            return this.query.replace(/page=\d+/, `page=${page}`);
        } else if (this.query.length){
            return `${this.query}&page=${page}`;
        } else {
            return `?page=${page}`;
        }
    }
}

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
            return new DataView(buffer);
        }).then(view => {
            const total_galleries = view.byteLength / 4;

            let page_navigator = new PageNavigator(Math.ceil(total_galleries / this.galleries_per_page));
            page_navigator.build();

            const results = [];
            for (let i = (this.page - 1) * this.galleries_per_page; i < Math.min( this.page * this.galleries_per_page, total_galleries); i++) {
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
            let result_length_element = document.querySelector("#result-length");
            result_length_element.innerText = data.length;
            result_length_element.parentElement.parentElement.removeAttribute("style");
            this.put(data);
        })
    }

    put(items) {
        document.querySelector("#loading-content").remove();
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