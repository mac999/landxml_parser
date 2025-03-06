const fs = require('fs');
const path = require('path');
const natural = require('natural');
const tokenizer = new natural.WordTokenizer();
const { parseString } = require('xml2js');

function importJson(fname) {
    let data = null;
    try {
        data = JSON.parse(fs.readFileSync(fname, 'utf8'));
    } catch (err) {
        console.error(err);
    }
    return data;
}

function getXmlTagName(tag) {
    const index = tag.indexOf("}");
    if (index >= 0) {
        tag = tag.substring(index + 1);
    }
    return tag;
}

function getKeyInDict(dictData, index) {
    const keys = Object.keys(dictData);
    if (keys.length <= index) {
        return null;
    }
    return keys[index];
}

class XMLParser {
    constructor() {
        this._find = 0;
        this._nodes = [];
    }

    clearFinalNode() {
        this._nodes = [];
    }

    addFindAllNode(node) {
        for (const n of this._nodes) {
            if (n === node) {
                return;
            }
        }
        this._nodes.push(node);
    }

    isMatchAttrib(node, attr) {
        let i = 0;
        for (const key in attr) {
            try {
                const value = attr[key];
                if (node.attrib[key].indexOf(value) >= 0) {
                    continue;
                }
                return false;
            } catch {
                return false;
            }
            i++;
        }
        console.log("* matched. " + JSON.stringify(node.attrib));
        return true;
    }

    findAll(node, tag, attr = "") {
        for (const child of node.children) {
            try {
                if (child.tag.indexOf(tag) >= 0) {
                    if (this.isMatchAttrib(child, attr)) {
                        this.addFindAllNode(child);
                        return child;
                    }
                }
            } catch (error) {
                // Handle error if necessary
            }
            const result = this.findAll(child, tag, attr);
            if (result !== null) {
                this.addFindAllNode(child);
                return result;
            }
            this._find++;
        }
        return null;
    }
}

function loadXml(fpath) {
    return new Promise((resolve, reject) => {
        fs.readFile(fpath, 'utf-8', (err, data) => {
            if (err) {
                reject(err);
                return;
            }
            parseString(data, (err, result) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(result);
            });
        });
    });
}

class LandXML {
    constructor() {
        this._modelData = null;
    }

    async load(fpath) {
        try {
            const xmlData = await loadXml(fpath);

            const model = this.parsing(xmlData);
            this._modelData = model;
            return model;
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    getModelsData() {
        return this._modelData;
    }

    save(fpath) {
        try {
            if (this._modelData === null) {
                return false;
            }

            fs.writeFileSync(fpath, JSON.stringify(this._modelData, null, 2));
        } catch (error) {
            console.error(error);
        }
        return true;
    }

    getPointsInText(text) {
        const tokens = tokenizer.tokenize(text);
        const pcd = [];
        for (let i = 0; i < Math.round(tokens.length / 2); i++) {
            const x = parseFloat(tokens[i * 2]);
            const y = parseFloat(tokens[i * 2 + 1]);
            pcd.push([x, y]);
        }
        return pcd;
    }

    getAttribText(node) {
        const tag = this.getXmlTagName(node.tag);
        console.log(tag, node.attrib);
        const data = {};
        data[tag] = {};
        data[tag]['attrib'] = node.attrib;
        if (node.text === null) {
            data[tag]['text'] = "";
        } else {
            data[tag]['text'] = node.text.replace('\t', '').replace('\n', '');
        }
        data[tag]['list'] = [];

        return [tag, node.attrib, node.text, data];
    }

    parsingCurve(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);
            if (text !== null) {
                data[tag]['points'] = this.getPointsInText(text);
            }
            model.push(data);

            // Handling different tags, if necessary
            // if (tag.indexOf("Start") >= 0) {}
            // else if (tag.indexOf("Center") >= 0) {}
            // else if (tag.indexOf("End") >= 0) {}
            // else if (tag.indexOf("PI") >= 0) {}
        }

        return model;
    }

    parsingCurveSet(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("Line") >= 0 || child.tag.indexOf("Curve") >= 0) {
                model.push(data);
                this.parsingCurve(child, data[tag]['list']);
            }
        }

        return model;
    }

    parsingCrossSectSurf(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("PntList2D") >= 0) {
                data[tag]['points'] = this.getPointsInText(text);
                model.push(data);
            }
        }

        return model;
    }

    parsingDesignCrossSectSurf(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("CrossSectPnt") >= 0) {
                data[tag]['points'] = this.getPointsInText(text); // TBD
                model.push(data);
            }
        }

        return model;
    }

    parsingCrossSect(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("DesignCrossSectSurf") >= 0) {
                model.push(data);
                this.parsingDesignCrossSectSurf(child, data[tag]['list']);
            } else if (child.tag.indexOf("CrossSectSurf") >= 0) {
                model.push(data);
                this.parsingCrossSectSurf(child, data[tag]['list']);
            }
        }

        return model;
    }

    parsingCrossSects(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("CrossSect") >= 0) {
                model.push(data);
                this.parsingCrossSect(child, data[tag]['list']);
            }
        }

        return model;
    }

    parsingProfSurf(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("PntList2D") >= 0) {
                data[tag]['points'] = this.getPointsInText(text);
                model.push(data);
            }
        }

        return model;
    }

    parsingProfAlign(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("PVI") >= 0 || child.tag.indexOf("ParaCurve") >= 0) {
                data[tag]['points'] = this.getPointsInText(text);
                model.push(data);
            }
        }

        return model;
    }

    parsingProfile(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (child.tag.indexOf("ProfSurf") >= 0) {
                model.push(data);
                this.parsingProfSurf(child, data[tag]['list']);
            } else if (child.tag.indexOf("ProfAlign") >= 0) {
                model.push(data);
                this.parsingProfAlign(child, data[tag]['list']);
            }
        }

        return model;
    }

    parsingCoordGeom(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (tag.indexOf("CoordGeom") >= 0) {
                model.push(data);
                this.parsingCurveSet(child, data[tag]['list']);
            } else if (tag.indexOf("CrossSects") >= 0) {
                model.push(data);
                this.parsingCrossSects(child, data[tag]['list']);
            } else if (tag.indexOf("Profile") >= 0) {
                model.push(data);
                this.parsingProfile(child, data[tag]['list']);
            }
        }

        return model;
    }

    parsingAlignment(node, model) {
        for (const child of node.children) {
            const [tag, attrib, text, data] = this.getAttribText(child);

            if (tag.indexOf("Alignment") >= 0) {
                model.push(data);
                this.parsingCoordGeom(child, data[tag]['list']);
            }
        }

        return model;
    }

    parsing(node) {
        const model = [];

        try {
            for (const child of node.children) {
                const [tag, attrib, text, data] = this.getAttribText(child);

                if (tag.indexOf("Project") >= 0) {
                    // Handle Project parsing
                } else if (tag.indexOf("Units") >= 0) {
                    // Handle Units parsing
                } else if (tag.indexOf("Application") >= 0) {
                    // Handle Application parsing
                } else if (tag.indexOf("Alignments") >= 0) {
                    model.push(data);
                    this.parsingAlignment(child, data[tag]['list']);
                } else if (tag.indexOf("Roadways") >= 0) {
                    // Handle Roadways parsing
                } else if (tag.indexOf("Surfaces") >= 0) {
                    // Handle Surfaces parsing
                }
            }
        } catch (error) {
            console.error(error);
        }

        return model;
    }
}

// Define test function
function test() {
    const parser = new LandXML();
    // Load landxml file
    // const model = parser.load('landxml_railway_sample.xml'); // Load railway landxml file
    const model = parser.load('./landxml_road_sample.xml'); // Load road landxml file
    console.log(model);
    // Save model data to JSON file
    parser.save('output_landxml.json');
}

// Check if the script is run directly
if (require.main === module) {
    test();
}


