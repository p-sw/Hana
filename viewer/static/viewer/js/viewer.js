var gg = {};
var successed = [];

class Viewer {
    init(galleryid) {
        this.galleryid = galleryid;

        this.drawer = document.querySelector('section#image');

        this.getGG().then(() => {
            this.getGalleryScript().then(files => {
                this.loadImages(files);
            });
        })
    }

    getGG() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            document.body.appendChild(script);
            script.onload = resolve;
            script.onerror = reject;
            script.async = true;
            script.src = '/api/get-js?url=https://ltn.hitomi.la/gg.js';
        });
    }

    getGalleryScript() {
        return fetch(`/api/get-js?url=https://ltn.hitomi.la/galleries/${this.galleryid}.js`, {
            method: 'GET',
            cache: 'force-cache',
        }).then(response => response.text()).then(data => {
            let file_regex = [/"files":\[[^\]]*\]/, /{[^}]*}/g];
            let files_raw = file_regex[0].exec(data)[0].matchAll(file_regex[1]);

            let files = [];

            for (let file_raw of files_raw) {
                let width = /"width":(\d+)/.exec(file_raw[0]);
                let height = /"height":(\d+)/.exec(file_raw[0]);
                let hash = /"hash":"([0-9a-f]{64})"/.exec(file_raw[0]);
                let haswebp = /"haswebp":(\d)/.exec(file_raw[0]);
                let hasavif = /"hasavif":(\d)/.exec(file_raw[0]);
                let name = /"name":"([^"]+)"/.exec(file_raw[0]);

                let file;
                file = {
                    width: width[1],
                    height: height[1],
                    hash: hash[1],
                    haswebp: haswebp[1],
                    hasavif: hasavif[1],
                    name: name[1],
                };
                files.push(file);
            }

            return files;
        })
    }

    getGalleryImageURL(file, ext) {
        let m = /(..)(.)$/.exec(file.hash);
        let url_from_hash = `https://a.hitomi.la/${ext}/${gg.b}${parseInt(m[2]+m[1], 16).toString(10)}/${file.hash}.${ext}`;

        let retval = "a";

        let hash_match = /\/[0-9a-f]{61}([0-9a-f]{2})([0-9a-f])/.exec(url_from_hash);
        if (!hash_match) {
            retval = "a" + retval;
        } else {
            let g = parseInt(hash_match[2]+hash_match[1], 16);
            retval = String.fromCharCode(97 + gg.m(g)) + retval;
        }
        return url_from_hash.replace(/\/\/..?\.hitomi\.la\//, `//${retval}.hitomi.la/`);
    }

    loadImages(files) {
        for (let file of files) {
            let url = `/api/get-image?url=${this.getGalleryImageURL(file, "webp")}&gallery=${this.galleryid}`;
            let img = document.createElement('img');
            img.src = url;
            img.onerror = (e) => {
                // delayed retry
                setTimeout(() => {
                    if (/&t=/.test(e.target.src)) {
                        e.target.src = e.target.src.replace(/&t=\d+/, `&t=${Date.now()}`);
                    } else {
                        e.target.src = e.target.src + "&t=" + Date.now();
                    }
                }, 1500);
            }
            img.onload = (e) => {
                successed.push(files.indexOf(file));
            }
            if (file.hasavif) {
                let picture = document.createElement('picture')
                let source_url = `/api/get-image?url=${this.getGalleryImageURL(file, "avif")}`;
                let source = document.createElement("source");
                source.setAttribute("srcset", source_url);
                source.setAttribute("type", "image/avif");
                picture.appendChild(source);
                picture.appendChild(img);
                this.drawer.appendChild(picture);
            } else {
                this.drawer.appendChild(img);
            }
        }
    }
}