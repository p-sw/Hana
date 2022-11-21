function loadErrorHandler(e) {
    setTimeout(() => {
        if (/&t=/.test(e.target.src)) {
            e.target.src = e.target.src.replace(/&t=\d+/, `&t=${Date.now()}`);
        } else {
            e.target.src = e.target.src + "&t=" + Date.now();
        }
    }, 1500);
}

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

class SearchObject {
    constructor(caller) {
        this.caller = caller;
    }

    entrypoint() {
        new Promise((resolve, reject) => {
            // first result
            if (!this.caller.positives.length) {
                this.caller.load(
                    this.caller.objToQuery({area: '', tag: 'index', language: 'all'})
                ).then((data) => {
                    resolve(data);
                })
            } else {
                let first = this.caller.positives.shift()
                this.caller.loadFull(
                    this.caller.objToQuery(
                        this.tag_processor(
                            first
                        )
                    )
                ).then((data) => {
                    resolve(data);
                })
            }
        }).then((data) => {
            // positive
            if (this.caller.positives.length) {
                return Promise.all(this.caller.positives.map(tag => {
                    return new Promise((resolve, reject) => {
                        this.caller.loadFull(
                            this.caller.objToQuery(
                                this.tag_processor(tag)
                            )
                        ).then(new_results => {
                            const new_results_set = new Set(new_results);
                            resolve(data.filter(gallery => new_results_set.has(gallery)));
                        });
                    });
                }));
            } else {
                return data;
            }
        }).then((data) => {
            if (typeof(data[0]) === "object") {
                data = data[0]
            }
            // negative
            if (this.caller.negatives.length) {
                return Promise.all(this.caller.negatives.map(tag => {
                   return new Promise((resolve, reject) => {
                       this.caller.loadFull(
                           this.caller.objToQuery(
                               this.tag_processor(tag)
                           )
                       ).then(new_results => {
                           const new_results_set = new Set(new_results);
                           resolve(data.filter(gallery => !new_results_set.has(gallery)));
                       });
                   });
                }));
            } else {
                return data;
            }
        }).then((data) => {
            if (typeof(data[0]) === "object") {
                data = data[0];
            }
            let result_length_element = document.querySelector("#result-length");
            result_length_element.innerText = data.length.toString();
            result_length_element.parentElement.parentElement.removeAttribute("style");

            this.caller.buildPageNav(data.length, this.caller.galleries_per_page);

            this.caller.put(data.slice((this.caller.page - 1) * this.caller.galleries_per_page, this.caller.page * this.caller.galleries_per_page));
        })
    }

    tag_processor(tag) {
        const sides = tag.split(":");
        const ns = sides[0];
        let tag_r = sides[1];

        let area = ns;
        let language = "all";
        if (ns === "female" || ns === "male") {
            area = "tag";
            tag_r = tag;
        } else if (ns === "language") {
            area = '';
            language = tag_r;
            tag_r = 'index';
        }

        return {'area': area, 'tag': tag_r, 'language': language};
    }
}

class FavoriteObject {
    constructor(caller) {
        this.caller = caller;
    }

    entrypoint() {
        this.load().then((data) => {
            let result_length_element = document.querySelector("#result-length");
            result_length_element.innerText = this.total_galleries;
            result_length_element.parentElement.parentElement.removeAttribute("style");

            this.caller.buildPageNav(this.total_galleries, this.caller.galleries_per_page);
            this.caller.put(data);
        })
    }

    load() {
        return fetch("/api/favorite/get-list", {
            method: "GET",
        }).then((response) => {
            if (response.status === 403) {
                window.location.href = '/';
            } else if (response.status !== 200) {
                window.location.reload();
            } else {
                return response.json();
            }
        }).then((data) => {
            this.total_galleries = data["galleries"].length;
            return data["galleries"].slice(
                (this.caller.page - 1) * this.caller.galleries_per_page,
                Math.min(this.total_galleries, this.caller.page * this.caller.galleries_per_page)
            );
        })
    }
}

class GalleryBlock {
    constructor(page_mode) {
        this.page_mode = page_mode;
        this.galleries_per_page = 25;
        this.query = decodeURIComponent(window.location.search);
        if (/[?&]page=\d+$/.test(this.query)) {
            this.page = parseInt(/[?&]page=(\d+)/.exec(this.query)[1], 10);
        } else {
            this.page = 1;
        }

        if (this.page_mode === "search") {
            this.query_tags = Array.prototype.map.call([...this.query.matchAll(/[+\-][a-z_:]+/g)], (match) => match[0]);
            if (this.query_tags) {
                this.positives = [];
                this.negatives = [];
                for (let tag of this.query_tags) {
                    if (tag[0] === "+") {
                        this.positives.push(tag.slice(1).replace(/_/g, " "));
                    } else if (tag[0] === "-") {
                        this.negatives.push(tag.slice(1).replace(/_/g, " "));
                    }
                }
            } else {
                window.location.href = '/';
            }
        }
    }

    entrypoint() {
        if (this.page_mode === "search") {
            new SearchObject(this).entrypoint();
        } else if (this.page_mode === "index") {
            this.load('').then((gallery_ids) => {
                this.buildPageNav(this.total_galleries, this.galleries_per_page);
                this.put(gallery_ids);
            });
        } else if (this.page_mode === "favorites") {
            new FavoriteObject(this).entrypoint();
        }
    }

    load(query) {
        return fetch(`/api/get-nozomi${query}`, {
            method: 'GET',
        }).then(response => {
            if (response.status === 200 || response.status === 206) {
                return response.arrayBuffer();
            } else {
                // reject
                return Promise.reject(response.status);
            }
        }).then((buffer) => {
            return new DataView(buffer);
        }, (code) => {
            if (code === 404) {
                document.querySelector("#loading-content").remove();
                document.querySelector("#gallery").innerHTML = "<p>404 에러<br>관리자에게 문의하세요.</p>";
            } else if (code === 500) {
                document.querySelector("#loading-content").remove();
                document.querySelector("#gallery").innerHTML = "<p>500 에러<br>잠시 후 다시 시도해보세요.</p>";
            } else {
                document.querySelector("#loading-content").remove();
                document.querySelector("#gallery").innerHTML = `<p>${code} 에러<br>관리자에게 문의하세요.</p>`;
            }
        }).then((data) => {
            this.total_galleries = data.byteLength / 4;

            let result = [];
            for (let i=(this.page - 1) * this.galleries_per_page;i<Math.min(this.total_galleries, this.galleries_per_page * this.page);i++) {
                result.push(data.getUint32(i*4, false));
            }
            return result;
        })
    }

    loadFull(query) {
        return fetch(`/api/get-nozomi${query}`, {
            method: 'GET',
        }).then(response => {
            if (response.status === 200 || response.status === 206) {
                return response.arrayBuffer();
            } else {
                // reject
                return Promise.reject(response.status);
            }
        }).then((buffer) => {
            return new DataView(buffer);
        }, (code) => {
            if (code === 404) {
                document.querySelector("#loading-content").remove();
                document.querySelector("#gallery").innerHTML = "<p>404 에러<br>관리자에게 문의하세요.</p>";
            } else if (code === 500) {
                document.querySelector("#loading-content").remove();
                document.querySelector("#gallery").innerHTML = "<p>500 에러<br>잠시 후 다시 시도해보세요.</p>";
            } else {
                document.querySelector("#loading-content").remove();
                document.querySelector("#gallery").innerHTML = `<p>${code} 에러<br>관리자에게 문의하세요.</p>`;
            }
        }).then((data) => {
            this.total_galleries = data.byteLength / 4;

            let result = [];
            for (let i=0;i < this.total_galleries;i++) {
                result.push(data.getUint32(i*4, false));
            }
            return result;
        })
    }

    buildPageNav(total_galleries, galleries_per_page) {
        let page_navigator = new PageNavigator(Math.ceil(total_galleries / galleries_per_page));
        page_navigator.build();
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
                // set a link to viewer (a.lillie, h1.lillie a)
                block.querySelector("div a.lillie").href = `/view/${id}`;
                block.querySelector("div h1.lillie a").href = `/view/${id}`;
                for (let as of block.querySelectorAll("div[class$=-content] a")) {
                    as.href = '';
                } /* IMPORTANT: TEMPORARY BLANKED, PROCESS IT LATER */
                // set a link to artists (div.artist-list a)
                const artists = block.querySelectorAll("div.artist-list a");
                for (let artist of artists) {
                    artist.href = `/app/search?tags=artist:${artist.innerText}`;
                }
                // set thumbnail
                let src = block.querySelector("div a.lillie div[class*=-img-cont] picture source");
                let img = block.querySelector("div a.lillie div[class*=-img-cont] picture img");
                if (src) {
                    src.src = "/api/get-image?url=https:"+/(\S+)\s1x/.exec(src.dataset.srcset)[1];
                    src.classList.add("lazyload");
                    src.addEventListener("error", loadErrorHandler);
                }
                if (img) {
                    img.src = "/api/get-image?url=https:"+img.dataset.src;
                    img.classList.add("lazyload");
                    img.addEventListener("error", loadErrorHandler);
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

    objToQuery(obj) {
        let result = [];
        for (let key in obj) {
            result.push(`${key}=${obj[key]}`);
        }
        return "?"+result.join('&');
    }
}
