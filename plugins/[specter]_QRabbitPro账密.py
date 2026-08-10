//[pin:true]
//[title: QRabbitPro账密]
//[language: es5]
//[disable: false] 禁用开关，true表示禁用，false表示可用
//[rule: 账密] 
//[rule: 账密登录] 
//[rule: 账密登陆] 
//[rule: 账密检测] 
//[rule: 账密删除] 
//[rule: 账密清理] 
//[priority: 99999999] 优先级，数字越大表示优先级越高
//[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
//[icon: https://pic.ziyuan.wang/2023/12/10/guest_77c52d3e94aa7.png]图标链接地址，支持http和https
//[version: 1.2.0]版本号
//[author: specter]作者,可以自定义，不定义的话，上传时会增加为aut云注册的用户名,收费插件一定要填写aut云账号
//[service: 2607401955]售后联系方式，service不完整，将不会审核上架
//[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 1.88] 上架价格
//[description: 指令：账密登录，账密检测，账密删除，账密清理。保证奥特曼为3.2.9以上版本和QRabbitPro为最新版(兔子次数限制为100次/日，谨慎购买），自行设置定时推送（计划任务）自动刷新（指令：账密检测），需要qls，jdNotify数据权限。] 使用方法尽量写具体
//[param: {"required":true,"key":"QRabbitPro.QRabbitPro_url","bool":false,"placeholder":"输入兔子的地址","name":"兔子的地址","desc":"输入兔子的地址,例如：https://192.168.1.1:5701"}]
//[param: {"required":true,"key":"AutoJdck.QLSName","bool":false,"placeholder":"青龙面板配置","name":"保存的青龙","desc":"输入奥特曼后台的容器管理中的名称，记得打开qls权限"}]
//[param: {"required":true,"key":"QRabbitPro.QRabbitPro_BotApiToken","bool":false,"placeholder":"输入兔子的机器人对接Token","name":"兔子的机器人对接Token","desc":"输入兔子的机器人对接Token(在RabbitPro的后台管理面板-登录-左边选择“配置文件”-最底下那行“机器人对接Token”,自己随便设置32位的字符并填到这里，不是RabbitToken！！！！"}]
//[param: {"required":true,"key":"AutoJdck.CKdelay","bool":false,"placeholder":"检测更新延迟（秒）","name":"检测更新延迟（秒）","desc":"检测ck是否有效的延迟（秒），默认1秒"}]
//[param: {"required":false,"key":"AutoJdck.errTip","bool":false,"placeholder":"续期触发短信推送提示","name":"续期触发短信推送提示","desc":"续期触发短信推送提示，不填则默认：账密续期失败了，请重新使用账密登录"}]
//[param: {"required":true,"key":"AutoJdck.userPush","bool":true,"placeholder":"开启续期成功后推送用户","name":"开启续期成功后推送用户","desc":"开启续期成功后推送用户"}]
//[param: {"required":true,"key":"AutoJdck.closeBadPush","bool":true,"placeholder":"关闭续期失败后推送用户","name":"关闭续期失败后推送用户","desc":"关闭续期失败后推送用户"}]
//[param: {"required":true,"key":"AutoJdck.closeBadAdmin","bool":true,"placeholder":"关闭续期失败后推送管理员","name":"关闭续期失败后推送管理员","desc":"关闭续期失败后推送管理员"}]
//[param: {"required":false,"key":"AutoJdck.failedLoginThreshold","bool":false,"placeholder":"0","name":"登录失败删除阈值","desc":"用户登录失败多少次后自动删除桶数据，默认0次（0表示不删除）"}]


// SHA-512 实现
class SHA512 {
    static #K = [
        0x428a2f98d728ae22n, 0x7137449123ef65cdn, 0xb5c0fbcfec4d3b2fn, 0xe9b5dba58189dbbcn,
        0x3956c25bf348b538n, 0x59f111f1b605d019n, 0x923f82a4af194f9bn, 0xab1c5ed5da6d8118n,
        0xd807aa98a3030242n, 0x12835b0145706fben, 0x243185be4ee4b28cn, 0x550c7dc3d5ffb4e2n,
        0x72be5d74f27b896fn, 0x80deb1fe3b1696b1n, 0x9bdc06a725c71235n, 0xc19bf174cf692694n,
        0xe49b69c19ef14ad2n, 0xefbe4786384f25e3n, 0x0fc19dc68b8cd5b5n, 0x240ca1cc77ac9c65n,
        0x2de92c6f592b0275n, 0x4a7484aa6ea6e483n, 0x5cb0a9dcbd41fbd4n, 0x76f988da831153b5n,
        0x983e5152ee66dfabn, 0xa831c66d2db43210n, 0xb00327c898fb213fn, 0xbf597fc7beef0ee4n,
        0xc6e00bf33da88fc2n, 0xd5a79147930aa725n, 0x06ca6351e003826fn, 0x142929670a0e6e70n,
        0x27b70a8546d22ffcn, 0x2e1b21385c26c926n, 0x4d2c6dfc5ac42aedn, 0x53380d139d95b3dfn,
        0x650a73548baf63den, 0x766a0abb3c77b2a8n, 0x81c2c92e47edaee6n, 0x92722c851482353bn,
        0xa2bfe8a14cf10364n, 0xa81a664bbc423001n, 0xc24b8b70d0f89791n, 0xc76c51a30654be30n,
        0xd192e819d6ef5218n, 0xd69906245565a910n, 0xf40e35855771202an, 0x106aa07032bbd1b8n,
        0x19a4c116b8d2d0c8n, 0x1e376c085141ab53n, 0x2748774cdf8eeb99n, 0x34b0bcb5e19b48a8n,
        0x391c0cb3c5c95a63n, 0x4ed8aa4ae3418acbn, 0x5b9cca4f7763e373n, 0x682e6ff3d6b2b8a3n,
        0x748f82ee5defb2fcn, 0x78a5636f43172f60n, 0x84c87814a1f0ab72n, 0x8cc702081a6439ecn,
        0x90befffa23631e28n, 0xa4506cebde82bde9n, 0xbef9a3f7b2c67915n, 0xc67178f2e372532bn,
        0xca273eceea26619cn, 0xd186b8c721c0c207n, 0xeada7dd6cde0eb1en, 0xf57d4f7fee6ed178n,
        0x06f067aa72176fban, 0x0a637dc5a2c898a6n, 0x113f9804bef90daen, 0x1b710b35131c471bn,
        0x28db77f523047d84n, 0x32caab7b40c72493n, 0x3c9ebe0a15c9bebcn, 0x431d67c49c100d4cn,
        0x4cc5d4becb3e42b6n, 0x597f299cfc657e2an, 0x5fcb6fab3ad6faecn, 0x6c44198c4a475817n
    ];

    static #Ch(x, y, z) {
        return (x & y) ^ (~x & z);
    }

    static #Maj(x, y, z) {
        return (x & y) ^ (x & z) ^ (y & z);
    }

    static #Σ0(x) {
        return (this.#rotateRight(x, 28n) ^ this.#rotateRight(x, 34n) ^ this.#rotateRight(x, 39n));
    }

    static #Σ1(x) {
        return (this.#rotateRight(x, 14n) ^ this.#rotateRight(x, 18n) ^ this.#rotateRight(x, 41n));
    }

    static #σ0(x) {
        return (this.#rotateRight(x, 1n) ^ this.#rotateRight(x, 8n) ^ (x >> 7n));
    }

    static #σ1(x) {
        return (this.#rotateRight(x, 19n) ^ this.#rotateRight(x, 61n) ^ (x >> 6n));
    }

    static #rotateRight(x, n) {
        return ((x >> n) | (x << (64n - n))) & 0xffffffffffffffffn;
    }

    static hash(message) {
        // 初始哈希值
        let H = [
            0x6a09e667f3bcc908n, 0xbb67ae8584caa73bn,
            0x3c6ef372fe94f82bn, 0xa54ff53a5f1d36f1n,
            0x510e527fade682d1n, 0x9b05688c2b3e6c1fn,
            0x1f83d9abfb41bd6bn, 0x5be0cd19137e2179n
        ];

        // 预处理消息
        const bytes = new Uint8Array(message);
        const bitLength = BigInt(bytes.length * 8);
        const padding = new Uint8Array(128 - (bytes.length + 17) % 128 + 17);
        padding[0] = 0x80;

        // 添加消息长度（以比特为单位）
        for (let i = padding.length - 16; i < padding.length; i++) {
            padding[i] = Number((bitLength >> BigInt(8 * (padding.length - 1 - i))) & 0xffn);
        }

        // 处理消息块
        const blocks = new Uint8Array([...bytes, ...padding]);

        for (let i = 0; i < blocks.length; i += 128) {
            const W = new Array(80).fill(0n);

            // 准备消息调度
            for (let t = 0; t < 16; t++) {
                W[t] = 0n;
                for (let j = 0; j < 8; j++) {
                    W[t] = (W[t] << 8n) | BigInt(blocks[i + t * 8 + j]);
                }
            }

            for (let t = 16; t < 80; t++) {
                W[t] = this.#σ1(W[t - 2]) + W[t - 7] + this.#σ0(W[t - 15]) + W[t - 16];
                W[t] = W[t] & 0xffffffffffffffffn;
            }

            // 初始化工作变量
            let [a, b, c, d, e, f, g, h] = H;

            // 主循环
            for (let t = 0; t < 80; t++) {
                const T1 = h + this.#Σ1(e) + this.#Ch(e, f, g) + this.#K[t] + W[t];
                const T2 = this.#Σ0(a) + this.#Maj(a, b, c);

                h = g;
                g = f;
                f = e;
                e = (d + T1) & 0xffffffffffffffffn;
                d = c;
                c = b;
                b = a;
                a = (T1 + T2) & 0xffffffffffffffffn;
            }

            // 计算中间哈希值
            H[0] = (H[0] + a) & 0xffffffffffffffffn;
            H[1] = (H[1] + b) & 0xffffffffffffffffn;
            H[2] = (H[2] + c) & 0xffffffffffffffffn;
            H[3] = (H[3] + d) & 0xffffffffffffffffn;
            H[4] = (H[4] + e) & 0xffffffffffffffffn;
            H[5] = (H[5] + f) & 0xffffffffffffffffn;
            H[6] = (H[6] + g) & 0xffffffffffffffffn;
            H[7] = (H[7] + h) & 0xffffffffffffffffn;
        }

        // 转换为字节数组
        const result = new Uint8Array(64);
        for (let i = 0; i < 8; i++) {
            const value = H[i];
            for (let j = 0; j < 8; j++) {
                result[i * 8 + j] = Number((value >> BigInt(56 - j * 8)) & 0xffn);
            }
        }

        return result;
    }
}

// AES S-box
const SBOX = new Uint8Array([
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]);

class AES {
    constructor(key) {
        this.key = key;
        this.expandedKey = this.expandKey();
    }

    expandKey() {
        const Nk = 8; // 密钥长度(32字节 = 256位)
        const Nr = 14; // 轮数
        const expandedKey = new Uint8Array((Nr + 1) * 16);
        expandedKey.set(this.key);

        for (let i = Nk; i < expandedKey.length / 4; i++) {
            let temp = expandedKey.slice((i - 1) * 4, i * 4);

            if (i % Nk === 0) {
                temp = this.subWord(this.rotWord(temp));
                temp[0] ^= this.rcon(i / Nk);
            } else if (Nk > 6 && i % Nk === 4) {
                temp = this.subWord(temp);
            }

            for (let j = 0; j < 4; j++) {
                expandedKey[i * 4 + j] = expandedKey[(i - Nk) * 4 + j] ^ temp[j];
            }
        }
        return expandedKey;
    }

    encryptBlock(block) {
        const state = new Uint8Array(16);
        state.set(block);

        this.addRoundKey(state, 0);

        for (let round = 1; round < 14; round++) {
            this.subBytes(state);
            this.shiftRows(state);
            this.mixColumns(state);
            this.addRoundKey(state, round);
        }

        this.subBytes(state);
        this.shiftRows(state);
        this.addRoundKey(state, 14);

        return state;
    }

    subBytes(state) {
        for (let i = 0; i < 16; i++) {
            state[i] = SBOX[state[i]];
        }
    }

    shiftRows(state) {
        const temp = new Uint8Array(16);
        temp.set(state);

        // 第二行左移1位
        state[1] = temp[5];
        state[5] = temp[9];
        state[9] = temp[13];
        state[13] = temp[1];

        // 第三行左移2位
        state[2] = temp[10];
        state[6] = temp[14];
        state[10] = temp[2];
        state[14] = temp[6];

        // 第四行左移3位
        state[3] = temp[15];
        state[7] = temp[3];
        state[11] = temp[7];
        state[15] = temp[11];
    }

    mixColumns(state) {
        for (let i = 0; i < 16; i += 4) {
            const s0 = state[i];
            const s1 = state[i + 1];
            const s2 = state[i + 2];
            const s3 = state[i + 3];

            state[i] = this.mul(0x02, s0) ^ this.mul(0x03, s1) ^ s2 ^ s3;
            state[i + 1] = s0 ^ this.mul(0x02, s1) ^ this.mul(0x03, s2) ^ s3;
            state[i + 2] = s0 ^ s1 ^ this.mul(0x02, s2) ^ this.mul(0x03, s3);
            state[i + 3] = this.mul(0x03, s0) ^ s1 ^ s2 ^ this.mul(0x02, s3);
        }
    }

    addRoundKey(state, round) {
        const roundKey = this.expandedKey.slice(round * 16, (round + 1) * 16);
        for (let i = 0; i < 16; i++) {
            state[i] ^= roundKey[i];
        }
    }

    mul(a, b) {
        let p = 0;
        let hiBitSet;
        for (let i = 0; i < 8; i++) {
            if ((b & 1) !== 0) {
                p ^= a;
            }
            hiBitSet = (a & 0x80) !== 0;
            a <<= 1;
            if (hiBitSet) {
                a ^= 0x1b;
            }
            b >>= 1;
        }
        return p & 0xff;
    }

    rotWord(word) {
        return new Uint8Array([word[1], word[2], word[3], word[0]]);
    }

    subWord(word) {
        return new Uint8Array(word.map(b => SBOX[b]));
    }

    rcon(i) {
        let value = 1;
        for (let j = 0; j < i - 1; j++) {
            value = this.mul(value, 2);
        }
        return value;
    }

    // GCM模式加密
    encryptGCM(plaintext, nonce) {
        // 初始化H (H = AES-ECB(K, 0^128))
        const H = this.encryptBlock(new Uint8Array(16));

        // 初始化J0
        const J0 = new Uint8Array(16);
        J0.set(nonce);
        J0[15] = 1;

        // 加密计数器生成密钥流
        const ciphertext = new Uint8Array(plaintext.length);
        let counter = new Uint8Array(J0);

        for (let i = 0; i < plaintext.length; i += 16) {
            counter[15]++;
            const keyStream = this.encryptBlock(counter);
            const blockSize = Math.min(16, plaintext.length - i);

            for (let j = 0; j < blockSize; j++) {
                ciphertext[i + j] = plaintext[i + j] ^ keyStream[j];
            }
        }

        // 计算认证标签
        const tag = this.generateGCMTag(H, J0, plaintext, ciphertext);

        return {
            ciphertext,
            tag
        };
    }

    generateGCMTag(H, J0, plaintext, ciphertext) {
        // GHASH计算
        let X = new Uint8Array(16);

        // 处理密文
        for (let i = 0; i < ciphertext.length; i += 16) {
            const block = ciphertext.slice(i, Math.min(i + 16, ciphertext.length));
            for (let j = 0; j < block.length; j++) {
                X[j] ^= block[j];
            }
            X = this.ghashMul(X, H);
        }

        // 处理长度
        const lenA = 0; // 无附加认证数据
        const lenC = BigInt(ciphertext.length * 8);
        const lenBlock = new Uint8Array(16);
        for (let i = 8; i < 16; i++) {
            lenBlock[i] = Number((lenC >> BigInt(8 * (15 - i))) & 0xffn);
        }

        for (let i = 0; i < 16; i++) {
            X[i] ^= lenBlock[i];
        }
        X = this.ghashMul(X, H);

        // 生成最终标签
        const tag = this.encryptBlock(J0);
        for (let i = 0; i < 16; i++) {
            tag[i] ^= X[i];
        }

        return tag;
    }

    ghashMul(X, H) {
        let Z = new Uint8Array(16);
        let V = new Uint8Array(H);

        for (let i = 0; i < 16; i++) {
            for (let j = 7; j >= 0; j--) {
                if ((X[i] & (1 << j)) !== 0) {
                    for (let k = 0; k < 16; k++) {
                        Z[k] ^= V[k];
                    }
                }

                const carry = (V[15] & 1) === 1;
                for (let k = 15; k > 0; k--) {
                    V[k] = (V[k] >>> 1) | ((V[k - 1] & 1) << 7);
                }
                V[0] = V[0] >>> 1;

                if (carry) {
                    V[0] ^= 0xe1;
                }
            }
        }

        return Z;
    }
}

// 安全随机数生成
function getRandomBytes(length) {
    const array = new Uint8Array(length);
    for (let i = 0; i < length; i++) {
        array[i] = Math.floor(Math.random() * 256);
    }
    return array;
}

// 简单的 TextEncoder 实现
class TextEncoder {
    encode(str) {
        const arr = new Uint8Array(str.length);
        for (let i = 0; i < str.length; i++) {
            arr[i] = str.charCodeAt(i) & 0xff;
        }
        return arr;
    }
}

// Base64 编码实现
function btoa(str) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let out = '';
    let i = 0;
    let len = str.length;

    while (i < len) {
        const c1 = str.charCodeAt(i++) & 0xff;
        if (i === len) {
            out += chars.charAt(c1 >> 2);
            out += chars.charAt((c1 & 0x3) << 4);
            out += '==';
            break;
        }
        const c2 = str.charCodeAt(i++);
        if (i === len) {
            out += chars.charAt(c1 >> 2);
            out += chars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
            out += chars.charAt((c2 & 0xF) << 2);
            out += '=';
            break;
        }
        const c3 = str.charCodeAt(i++);
        out += chars.charAt(c1 >> 2);
        out += chars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
        out += chars.charAt(((c2 & 0xF) << 2) | ((c3 & 0xC0) >> 6));
        out += chars.charAt(c3 & 0x3F);
    }
    return out;
}

// 主加密函数
function encrypt_pwd_aes_gcm(pwd, account) {
    // 生成密钥
    const salt = "#(*():dfgjn^%&89$%#";
    const message = salt + account + salt;
    const textEncoder = new TextEncoder();
    const keyBytes = SHA512.hash(textEncoder.encode(message)).slice(0, 32);

    // 生成12字节的随机nonce
    const nonce = getRandomBytes(12);

    // 对密码进行填充
    const randomPrefix = getRandomBytes(16);
    const randomSuffix = getRandomBytes(16);
    const pwdBytes = textEncoder.encode(pwd);
    const padding = new Uint8Array([
        ...randomPrefix,
        ...pwdBytes,
        ...randomSuffix
    ]);

    // AES-GCM加密
    const aes = new AES(keyBytes);
    const { ciphertext, tag } = aes.encryptGCM(padding, nonce);

    // 组合tag + 加密数据 + nonce
    const finalArray = new Uint8Array([
        ...tag,
        ...ciphertext,
        ...nonce
    ]);

    // 转换为字符串后进行base64编码
    let str = '';
    for (let i = 0; i < finalArray.length; i++) {
        str += String.fromCharCode(finalArray[i]);
    }
    return btoa(str);
}

var actongzi = 'AutoJdck'
var acUrl = bucketGet('QRabbitPro', "QRabbitPro_url");
var botApiToken = bucketGet('QRabbitPro', "QRabbitPro_BotApiToken");
var user = GetUserID();
var platform = GetImType();
var chatId = GetChatID()
var Content = GetContent();
var Admin = isAdmin();
var isAuto = false;
var userPush = bucketGet(actongzi, "userPush");
let qltokens = ''

var QLS = null;
try {
    QLS = [];
    const array = bucketKeys('qls');

    if (!array || array.length === 0) {
        notifyMasters("未找到任何青龙容器配置");
    }

    for (const item of array) {
        try {
            let data = bucketGet('qls', item);
            if (!data) {
                Debug(`容器 ${item} 的配置数据为空`);
                continue;
            }

            const parsedData = JSON.parse(data);
            if (!parsedData.host || !parsedData.client_id || !parsedData.client_secret) {
                Debug(`容器 ${item} 配置数据不完整: ${JSON.stringify(parsedData)}`);
                continue;
            }

            QLS.push(parsedData);
        } catch (parseError) {
            Debug(`解析容器 ${item} 配置失败: ${parseError.message}`);
        }
    }

    if (QLS.length === 0) {
        notifyMasters("没有有效的青龙容器配置");
    }

    Debug(`成功加载 ${QLS.length} 个青龙容器配置`);

} catch (error) {
    const errorMsg = `青龙容器配置加载失败: ${error.message}\n请确保：\n1. 插件已打开 qls 数据访问权限\n2. 青龙容器配置正确`;
    notifyMasters(errorMsg);
    QLS = [];
}

function AccountMain() {
    actongzi = 'AutoJdck'
    acUrl = bucketGet('QRabbitPro', "QRabbitPro_url");
    botApiToken = bucketGet('QRabbitPro', "QRabbitPro_BotApiToken");
    if (acUrl[acUrl.length - 1] == '/') {
        acUrl = acUrl.substring(0, acUrl.length - 1);
    }
    // urlList = (bucketGet(actongzi, "password_addr") || '').split(',');
    Debug(acUrl)
    user = GetUserID();
    platform = GetImType();
    chatId = GetChatID()
    Content = GetContent();
    isAuto = false;
    qltokens = ''

    if (!Content || Content == '账密检测') {
        isAuto = true;
        if (Admin) {
            cron()
        } else if (user) {
            let tongzipin = getUserPin()
            if (tongzipin) {
                cron(tongzipin)
            } else {
                return
            }
        }
    } else if (Content == '账密删除' && Admin) {
        DeleteAccount();
    } else if (Content == '账密清理' && Admin) {
        CleanAccount();
    } else if (Content == '账密同步' && Admin) {
        SyncAccount();
    } else if (Content == '账密登录' || Content == '账密登陆' || Content == '账密') {
        AccountSecret()
    }
}

function DeleteAccount() {
    sendText('请输入要删除的pin')
    let msg = ShuRu()
    if (msg) {
        bucketDel(actongzi, msg)
        sendText(`删除${msg}成功`)
    }
}

function SyncAccount() {
    let QLS = bucketGet(actongzi, "qls");
    if (!QLS) {
        notifyMasters(`账密未配置青龙信息，请前往插件配参填写。未填写青龙时使用此功能会导致账号改绑。`);
        return
    }

    let arr = []
    let keys = bucketKeys(actongzi)
    for (const pin of keys) {
        let record = bucketGet(actongzi, pin)
        if (record.indexOf("password") === -1) {
            continue
        } else {
            record = JSON.parse(record)
            if (record.cookie) {
                arr.push(pin)
            }
        }
    }
    if (arr.length > 0) {
        for (const pin of arr) {
            let data = bucketGet(actongzi, pin)
            let record = JSON.parse(data)
            ckSubmit(record.cookie, pin)
        }
    }
}

function CleanAccount() {
    let arr = []

    let keys = bucketKeys(actongzi)
    for (const pin of keys) {
        let record = bucketGet(actongzi, pin)
        if (record.indexOf("password") === -1) {
            continue
        } else {
            record = JSON.parse(record)
            if (!record.cookie) {
                arr.push(pin)
            }
        }
    }
    if (arr.length > 0) {
        sendText(`以下账号没有cookie，将被删除：\n${arr.join('\n')}`)
        sendText(`是否确认删除？(y/n)`)
        let msg = ShuRu()
        if (msg == 'y') {
            for (const pin of arr) {
                bucketDel(actongzi, pin)
            }
            sendText(`清理完成`)
        }
    } else {
        sendText(`没有可清理的账号，输入"账密检测"重新检测`)
    }
}

function getUserPin() {
    // 绑定的京东账号
    const jds = bucketKeys("pin" + platform.toUpperCase(), user);

    // 如果没有绑定的账号
    if (jds.length === 0) {
        sendText('没有与你绑定的账号，请对我说："登陆"');
        return false;
    }

    // 获取自动绑定的账号
    const autoPin = bucketKeys(actongzi);
    const tongzipin = getCommonElements(jds, autoPin);

    // 如果没有找到绑定的账密
    if (tongzipin.length === 0) {
        sendText('没有找到与你绑定的账密，请对我说："账密登陆"');
        return false;
    }

    return tongzipin;
}

// 获取两个数组的交集
function getCommonElements(arr1, arr2) {
    return arr1.filter(element => arr2.includes(element));
}

async function getAccountList() {
    const array = bucketKeys(actongzi)
    const accountList = []
    for (let pin of array) {
        let record = bucketGet(actongzi, pin)
        if (record.indexOf("password") === -1) {
            continue
        }
        record = JSON.parse(record)
        if (record.user == user) {
            record.pin = pin
            accountList.push(record)
        }
    }
    if (accountList.length > 0) {
        const hidePhone = (phone) => {
            return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
        }
        const loginStatuses = await Promise.all(accountList.map(item => checkLogin(item.pin)))
        const strArr = accountList.map((item, index) =>
            `${index + 1}：${item.pin}（${hidePhone(item.account)}）${loginStatuses[index] ? `` : '（已掉线）'}`
        )
        strArr.unshift('请选择你的操作，输入数字\n0：新增账号 -数字删除')
        sendText(strArr.join('\n'))
        var msg = ShuRu()
        if (msg) {
            if (msg == 0) {
                AddAccount()
            } else if (msg.includes('-')) {
                let choose = msg.split('-')[1]
                bucketDel(actongzi, accountList[choose - 1].pin)
                sendText('删除成功')
            } else if (msg > 0 && msg <= accountList.length) {
                let { account, password, cookie, user, platform, pin } = accountList[msg - 1];

                // if (checkIsUse()) {
                //     return
                // }
                let res = await doLogin(account, password, user, platform, pin);
                if (res.msg) {
                    sendText(`登录失败，${res.msg}`)
                }
            }
        }
    } else {
        AddAccount()
    }
}

async function checkLogin(pin) {
    let jnStr = bucketGet("jdNotify", pin)
    // Debug(jnStr)
    if (!jnStr) {
        return false
    }
    const jn = JSON.parse(jnStr)
    let cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
    Debug(cookie)
    let isLogin = await isLoginByX1a0He(cookie)
    if (isLogin) {
        return true
    }
    return false
}

async function AddAccount() {
    sendText('请输入账户名或手机号')
    var account = ShuRu();
    if (account) {
        sendText('请输入密码')
        var password = ShuRu();
        if (password) {
            // if (checkIsUse()) {
            //     return
            // }
            let res = await doLogin(account, password, user, platform);
            if (res.msg) {
                sendText(`登录失败，${res.msg}`)
            }
        }
    }
}

function AccountSecret() {
    // if (checkIsUse()) {
    //     return
    // }

    if (!chatId) {
        getAccountList();
    } else {
        sendText("为了您的账户安全，请私聊机器人使用");
    }
}

function isMoreThanHalfHourLater(oldTimeStr, newTimeStr) {
    // 将时间字符串解析为Date对象
    const oldTime = new Date(oldTimeStr);
    const newTime = new Date(newTimeStr);

    // 获取时间差（以毫秒为单位）
    const timeDifference = newTime - oldTime;

    // 半小时的毫秒数
    const halfHourInMilliseconds = 30 * 60 * 1000;

    // 判断时间差是否大于半小时
    return timeDifference > halfHourInMilliseconds;
}

async function cron(tongzipin) {
    let success = []
    let fail = []

    let array = null
    if (tongzipin) {
        array = tongzipin
    } else {
        array = bucketKeys(actongzi);
    }

    sendText(`开始检测...`);
    let total = 0

    if (array && array.length > 0) {
        for (const pin of array) {
            let record = bucketGet(actongzi, pin)
            if (record.indexOf("password") === -1) {
                continue
            }
            total++
            Debug(`开始检索${pin}是否过期`)

            const rec = JSON.parse(record);
            const { account, password, cookie, user, platform } = rec;
            let jnStr = '{}'
            let jncookie = cookie
            try {
                jnStr = bucketGet("jdNotify", pin)
                // Debug(jnStr)
                const jn = JSON.parse(jnStr)
                jncookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
            } catch (error) {
                Debug('jdNotify插件权限未开')
                jncookie = cookie
            }

            //检查cookie是否过期
            let isLogin = false
            if (!jncookie) {
                isLogin = false
                Debug(`Cookie为空，尝试续期....\n`);
            } else {
                isLogin = await getnickname(jncookie);
                if (!isLogin) {
                    // Debug(`接口1检测失败，尝试使用接口2....\n`);
                    isLogin = await isLoginByX1a0He(jncookie);
                }
            }

            let delay = bucketGet(actongzi, 'CKdelay')
            if (delay) {
                delay = delay * 1000
            } else {
                delay = 1000
            }
            sleep(delay);

            if (isLogin) {
                bucketSet(actongzi, pin, JSON.stringify({ account, password, cookie: jncookie, user, platform }));
                continue
            }
            // if (isLogin) continue;
            try {
                Debug(`${pin}过期了，开始登录`);
                // await getIdle()
                let res = await doLogin(account, password, user, platform, pin);
                if (res.msg) {
                    let closeBadPush = bucketGet(actongzi, 'closeBadPush')
                    if (closeBadPush !== 'true') {
                        let errTip = bucketGet(actongzi, 'errTip') || '账密续期失败了，请重新使用账密登录'
                        push(
                            {
                                imType: platform,
                                userID: user,
                                // groupCode: groupCode,
                                content: `${pin}${errTip}`,
                            }
                        )
                    }

                    fail.push(`${pin}失败原因:${res.msg}`)
                    // notifyMasters(`${pin}失败原因:${res.msg}`);
                } else if (res === false) {
                    fail.push(`${pin}失败原因：处理超时,可能触发了新验证，请稍后重试`)
                } else {
                    success.push(pin)
                }
            } catch (e) {
                notifyMasters(`${pin}失败原因：${e}`);
                fail.push(`${pin}失败原因：${e}`)
            }

        }
        if (success.length + fail.length > 0) {
            if (!tongzipin) {
                notifyMasters(`总帐号：${total}个\n过期账号：${success.length + fail.length}个\n续期成功：${success.length}个\n续期失败：${fail.length}个`);
            } else {
                sendText(`总帐号：${total}个\n过期账号：${success.length + fail.length}个\n续期成功：${success.length}个\n续期失败：${fail.length}个`);
            }
        } else {
            sendText(`总帐号：${total}个\n过期账号：0个`);
        }
        let closeBadAdmin = bucketGet(actongzi, 'closeBadAdmin')
        if (fail.length > 0) {
            if (closeBadAdmin !== 'true') {
                notifyMasters(`失败账号:\n${fail.join('\n')}`);
            }
            fail.forEach(item => {
                if (item.includes("账号或密码不正确")) {
                    const pin = item.split("失败原因")[0]
                    bucketDel(actongzi, pin)
                    sendText(`账号${pin}账号或密码不正确，已从桶子中自动删除`)
                }
            })
        }
    }
}

function splitArrayIntoChunks(array, chunkSize) {
    let results = [];
    for (let i = 0; i < array.length; i += chunkSize) {
        results.push(array.slice(i, i + chunkSize));
    }
    return results;
}

function sendChunks(array) {
    let chunks = splitArrayIntoChunks(array, 100)
    chunks.forEach(item => {
        sendText(item.join('\n'))
        sleep(1000)
    })
}

function updatePtKey(cookie) {
    var pt_key_pattern = /pt_key=([^;]*)/;
    var pt_pin_pattern = /pt_pin=([^;]*)/;
    var pt_key_match = pt_key_pattern.exec(cookie);
    var pt_pin_match = pt_pin_pattern.exec(cookie);
    let data = bucketGet("jdNotify", pt_pin_match[1])
    if (data) {
        const originData = JSON.parse(data);
        originData.PtKey = pt_key_match[1];
        bucketSet("jdNotify", pt_pin_match[1], JSON.stringify(originData));
    } else {
        let info = { "ID": pt_pin_match[1], "Pet": false, "Fruit": false, "DreamFactory": false, "Note": "", "PtKey": pt_key_match[1], "AssetCron": "", "PushPlus": "", "LoginedAt": "2024-07-07T11:22:03+08:00", "ClientID": "uUUT8eVZ_x5c" }
        bucketSet("jdNotify", pt_pin_match[1], JSON.stringify(info));
    }
}

/**
 * 获取当前时间 格式：yyyy-MM-dd HH:MM:SS
 */
function getCurrentTime() {
    var date = new Date();//当前时间
    var month = zeroFill(date.getMonth() + 1);//月
    var day = zeroFill(date.getDate());//日
    var hour = zeroFill(date.getHours());//时
    var minute = zeroFill(date.getMinutes());//分
    var second = zeroFill(date.getSeconds());//秒

    //当前时间
    var curTime = date.getFullYear() + "-" + month + "-" + day
        + " " + hour + ":" + minute + ":" + second;

    return curTime;
}

function zeroFill(i) {
    if (i >= 0 && i <= 9) {
        return "0" + i;
    } else {
        return i;
    }
}

function switchql() {
    let container_id = ''
    try {
        request({
            url: acUrl + "/api/Config",
            method: "get",//网络请求方法get,post,put,delete
            timeOut: 30000//单位为毫秒ms，也可以都小写timeout
        }, function (error, response, header, body) {
            Debug(body)
            let b = JSON.parse(body);
            let list = b.data.list;
            for (const item of list) {
                if (checkql(item.container_id) > 0) {
                    container_id = item.container_id
                    return
                }
            }
            Debug('container_id:' + container_id)
        })
        if (container_id) {
            return container_id
        } else {
            notifyMasters('QRabbitPro没有可用容器')
            return false
        }
    } catch (error) {
        notifyMasters('获取QRabbitPro容器出错：' + error)
        return false
    }
}


function checkql(container_id) {
    let ckcount = ''
    request({
        url: acUrl + "/api/QLConfig?container_id=" + container_id,
        method: "get",//网络请求方法get,post,put,delete
        timeOut: 30000//单位为毫秒ms，也可以都小写timeout
    }, function (error, response, header, body) {
        Debug(body)
        let b = JSON.parse(body);
        ckcount = b.data.ckcount;
        Debug(container_id + 'container_id:' + ckcount)

    })
    return ckcount
}

function updateQR(ck) {
    let container_id = switchql()
    let body = request({
        url: acUrl + "/api/upload",
        method: "post",
        timeOut: 30000,
        body: {
            "ck": ck,
            "container_id": container_id
          }
    })
    Debug(body)
}

function ckSubmit(cookie, pin) {
    // QLS = bucketGet(actongzi, "qls");
    // pin = decodeURIComponent(pin)
    Debug(cookie, pin)
    updateQR(cookie)
    var QLSName = bucketGet(actongzi, "QLSName")
    QLSName = QLSName.split(',')
    QLS = QLS.filter(item => QLSName.includes(item.name))

    let DePin = decodeURIComponent(pin)
    // Debug(QLS)
    if (QLS) {
        let defaultIndex = QLS.findIndex(item => item.default)
        let isupdate = false;

        // 先尝试在所有容器中查找并更新
        for (const ql of QLS) {
            var id = SelectQLSCK(ql, pin);
            Debug(id);

            try {
                if (id != 0) {
                    // 找到已存在的记录，进行更新
                    var qlupdatebody = qlupdate(cookie, id, ql);
                    var qlupdatebodyjson = JSON.parse(qlupdatebody);
                    if (qlupdatebodyjson.code == "200") {
                        if (!isAuto) {
                            notifyMasters(`${DePin}更新成功`);
                        }
                        qlenable(ql.host, [id]);
                        isupdate = true;
                        break; // 更新成功后直接跳出循环
                    } else {
                        Debug(qlupdatebody);
                        notifyMasters(`${ql.host}更新${DePin}失败，请检查青龙配置。`);
                    }
                }
            } catch (e) {
                notifyMasters(e);
                notifyMasters(`${ql.host}更新${DePin}失败，请检查青龙配置。`);
            }
        }

        // 如果所有容器都没找到，需要新增
        if (!isupdate) {
            let targetQL;

            // 优先使用default为true的容器
            if (defaultIndex !== -1) {
                targetQL = QLS[defaultIndex];
            } else {
                // 没有default为true的容器，使用第一个容器
                targetQL = QLS[0];
            }

            if (targetQL) {
                try {
                    qltoken(targetQL.host, targetQL.client_id, targetQL.client_secret);
                    var qlinsertbody = qlinsert(cookie, targetQL, DePin);
                    var qlinsertbodyjson = JSON.parse(qlinsertbody);
                    if (qlinsertbodyjson.code == "200") {
                        if (!isAuto) {
                            notifyMasters(`${DePin}新增成功`);
                        }
                    } else {
                        Debug(qlinsertbody);
                        notifyMasters(`${targetQL.host}新增${DePin}失败，请检查青龙配置。`);
                    }
                } catch (e) {
                    notifyMasters(e);
                    notifyMasters(`${targetQL.host}新增${DePin}失败，请检查青龙配置。`);
                }
            }
        }
    } else {
        breakIn(cookie)
    }
}

function qlenable(host, ckid) {
    try {
        var body = request({
            url: host + "/open/envs/enable",
            method: "put",
            headers: {
                "Authorization": "Bearer " + qltokens,
            },
            body: ckid
        });
        Debug('qlenable()' + body);
    } catch (error) {
        Debug(error);
        notifyMasters(error);
    }
}

function getnickname(cookie) {
    let body = request({
        url: "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion",
        method: "Get",
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
            "Accept-Language": "zh-cn",
            "Referer": "https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&",
            "Cookie": cookie,
            "Accept": "*/*",
            "Host": "me-api.jd.com",
            "Connection": "keep-alive"
        }
    })
    try {
        let obj = JSON.parse(body);
        if (obj['retcode'] === "0" && obj.data && obj.data.hasOwnProperty("userInfo")) {
            // Debug('获取账户别名成功，')
            return true
        } else if (obj['retcode'] === "1001") {
            // Debug('cookie过期')
            return false
        } else {
            // Debug('服务器返回未知状态')
            return false
        }
    } catch (e) {
        Debug(e);
        return false
    }
}

async function isLoginByX1a0He(cookie) {
    try {
        let body = request({
            url: "https://plogin.m.jd.com/cgi-bin/ml/islogin",
            method: "get",
            headers: {
                Cookie: cookie,
                referer: "https://h5.m.jd.com/",
                "User-Agent": "jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            },
            timeout: 10000,
        });

        // 检查响应是否为空
        if (!body) {
            Debug('接口返回为空');
            return false;
        }

        // 解析JSON响应
        const data = JSON.parse(body);
        // Debug(body);

        // 使用严格相等进行比较
        if (data.islogin === "1") {
            return true;
        } else if (data.islogin === "0") {
            return false;
        }

        // 处理未知状态
        Debug(`未知的登录状态: ${JSON.stringify(data)}`);
        return false;

    } catch (error) {
        Debug(`发生错误: ${error.message}`);
        return false;
    }
}

function qlupdate(ck, id, QLS) {
    var body = request({
        url: QLS.host + "/open/envs",
        method: "put",
        body: Object.assign(typeof id === "number" ? {
            "id": id
        } : {
            "_id": id
        }, {
            "name": 'JD_COOKIE',
            "value": ck
        }),
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    return body;
}

function qlinsert(ck, QLS, remarks) {
    var body = request({
        url: QLS.host + "/open/envs",
        method: "post",
        body: [{
            "name": 'JD_COOKIE',
            "value": ck,
            "remarks": remarks,
        }],
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    return body;
}

function SelectQLSCK(QLS, envname) {
    try {
        qltoken(QLS.host, QLS.client_id, QLS.client_secret);
        let qlselectbody = qlselect(QLS.host, 'envs', envname);
        let qlckjson = JSON.parse(qlselectbody);

        if (qlckjson && qlckjson.data && Array.isArray(qlckjson.data)) {
            // 查找 name: "JD_COOKIE" 的值
            let jdCookie = qlckjson.data.find(item => item.name === "JD_COOKIE");

            if (jdCookie) {
                return jdCookie.id || jdCookie._id;
            }
        }

        return false;
    } catch (e) {
        Debug(e);
        return false;
    }
}

function qlselect(host, category, envname) {
    Debug(`${host}/open/${category}?searchValue=${envname}`)
    try {
        var body = request({
            url: `${host}/open/${category}?searchValue=${envname}`,
            method: "get",
            headers: {
                "Authorization": "Bearer " + qltokens,
            }
        });
        return body;
    } catch (e) {
        Debug(e)
    }
}

function qltoken(qldizhi, qlclient_id, qlclient_secret) {
    try {
        var body = request({
            url: qldizhi + "/open/auth/token?client_id=" + qlclient_id + "&client_secret=" + qlclient_secret,
            method: "get",
        });
        Debug('qltokens为' + body)
        var fhtoken = JSON.parse(body);
        qltokens = fhtoken.data.token;
    } catch (e) {
        Debug(e)
        qltokens = ''
    }
}

async function doLogin(account, password, user, platform, oldPin) {
    try {
        sendText(`开始登录账号${account}`);
        let res = await loginProcess(account, password);
        Debug(`loginProcess返回结果: ${JSON.stringify(res)}`);

        if (!res) {
            return {
                code: 4,
                msg: "登录过程返回为空"
            };
        }

        switch (res.code) {
            case 0:
                if (!res.ck || !res.pin) {
                    Debug(`登录成功但缺少必要信息: ${JSON.stringify(res)}`);
                    return {
                        code: 4,
                        msg: "登录成功但获取账号信息失败"
                    };
                }

                const cookie = res.ck;
                updatePtKey(cookie);
                const pin = res.pin;

                try {
                    await ckSubmit(cookie, pin);
                } catch (error) {
                    Debug(`ckSubmit执行失败: ${error.message}`);
                    // 继续执行，不影响登录结果
                }

                sendText(`${pin}登录成功`);

                if (isAuto && userPush == 'true') {
                    push({
                        imType: platform,
                        userID: user,
                        content: `${pin}续期成功`,
                    });
                }

                let info = { account, password, cookie, user, platform };
                bucketDel(actongzi, encodeURIComponent(pin));
                bucketSet(actongzi, pin, JSON.stringify(info));
                
                resetLoginFailureCount(account);

                if (!isAuto) {
                    notifyMasters(`======JD登陆通知======\n[登陆用户]：${user}\n[登陆平台]：${platform}\n[登陆账户]：${decodeURIComponent(pin)}\n[登陆方式]：账密登陆\n[登陆时间]：${getCurrentTime()}`);
                    bucketSet("pin" + platform.toUpperCase(), pin, user);
                }
                return pin;

            case 1:
                if (!isAuto) {
                    let ranks = JSON.parse(bucketGet(actongzi, "ranks") || '[]');
                    let existingRetry = ranks.find(item => item.account === account);

                    if (existingRetry) {
                        clearQueue(account);
                        sendText(`账号${account}风控，请重试账密登陆或者使用其他方式登陆`);
                        return {
                            code: 4,
                            msg: `账号${account}风控，请重试账密登陆或者使用其他方式登陆`
                        };
                    } else {
                        sendText(res.msg || "需要验证");
                        sendText("请点击上方链接完成验证，验证成功后页面是空白的返回即可，输入y重登。");
                        addRetry(account, password, user, platform);
                        return false;
                    }
                } else {
                    sendText(res.msg || "需要验证");
                    return res;
                }

            case 2:
                handleLoginFailure(account);
                sendText('登录失败: ' + (res.msg || "未知原因"));
                return res;

            default:
                handleLoginFailure(account);
                Debug(`未知的返回码: ${JSON.stringify(res)}`);
                return {
                    code: 4,
                    msg: res.msg || "登录过程发生未知错误"
                };
        }
    } catch (error) {
        handleLoginFailure(account);
        Debug(`doLogin执行出错: ${error.message}`);
        return {
            code: 4,
            msg: `登录过程发生错误: ${error.message}`
        };
    }
}

async function loginProcess(account, pwd) {
    try {
        // 1. 初始化
        const initRes = await init(account);
        if (!initRes.success) {
            if (initRes.code === 505) {
                return formatResponse(4, initRes.message || initRes.msg);
            }

            if (initRes.code === 666) {
                // 尝试图形验证码
                for (let i = 0; i < 5; i++) {
                    const captchaRes = await autoCaptcha(account);
                    if (captchaRes.success) break;

                    if (captchaRes.code === 505) {
                        return formatResponse(4, captchaRes.message || captchaRes.msg);
                    }

                    if (captchaRes.code !== 666) {
                        return formatResponse(4, captchaRes.message || captchaRes.msg);
                    }
                }
            } else {
                return formatResponse(4, initRes.message || initRes.msg);
            }
        }

        // 2. 登录
        const loginRes = await login(account, pwd);
        if (!loginRes.success) {
            // 处理不同登录错误情况
            switch (loginRes.code) {
                case 505:
                case 503:
                    return formatResponse(4, loginRes.message || loginRes.msg);

                case 555:
                    return formatResponse(1, loginRes.RiskUrl, '需要二次验证');

                case 601:
                case 602:
                    if (!isAuto) {
                        return handleRiskVerification(account);
                    }
                    return formatResponse(4, loginRes.message || loginRes.msg);

                default:
                    return formatResponse(4, loginRes.message || loginRes.msg);
            }
        }

        // 3. 登录成功
        return formatResponse(0, loginRes.message || loginRes.msg, null, {
            ck: loginRes.ck,
            pin: loginRes.pin
        });

    } catch (error) {
        Debug('登录过程发生错误:', error);
        return formatResponse(4, error.message);
    }
}

// 统一响应格式
function formatResponse(code, msg, data = null, extra = {}) {
    return {
        code,
        msg,
        data,
        ...extra
    };
}

async function handleRiskVerification(account) {
    // 发送风控请求
    const riskRes = await risk_send(account);

    if (!riskRes.success) {
        // 检查初始化状态
        if (riskRes.code === 505) {
            // 初始化失败，终止程序
            Debug(riskRes.message);
            return {
                code: 4,
                msg: riskRes.message
            }
        } else if (riskRes.code === 666) {
            // 初始化成功，但图形验证失败，尝试自动验证码
            for (let i = 0; i < 5; i++) {
                const riskAutoCaptchaRes = await risk_auto_captcha(account);

                if (riskAutoCaptchaRes.success) {
                    // 图形验证成功
                    break;
                }

                if (riskAutoCaptchaRes.code === 505) {
                    // 图形验证失败，无法继续尝试
                    Debug(riskAutoCaptchaRes.message);
                    return {
                        code: 4,
                        msg: riskAutoCaptchaRes.message
                    }
                } else if (riskAutoCaptchaRes.code === 666) {
                    // 图形验证失败，继续尝试
                    continue;
                } else {
                    // 其他错误
                    Debug(riskAutoCaptchaRes.message);
                    return {
                        code: 4,
                        msg: riskAutoCaptchaRes.message
                    }
                }
            }
        } else {
            // 其他错误
            Debug(riskRes.message);
            return {
                code: 4,
                msg: riskRes.message
            }
        }
    }

    // 获取用户输入的验证码
    sendText("请输入验证码")
    const code = ShuRu(90000);

    if (!code) {
        return {
            code: 4,
            msg: "验证码输入超时"
        }
    }

    // 验证码验证
    const riskVerifyRes = await risk_verify_code(account, code);

    if (!riskVerifyRes.success) {
        if (riskVerifyRes.code === 505) {
            // 登录失败
            Debug(riskVerifyRes.message);
            return {
                code: 4,
                msg: riskVerifyRes.message
            }
        } else if (riskVerifyRes.code === 503) {
            // 授权问题或京东账号问题
            Debug(riskVerifyRes.message);
            return {
                code: 4,
                msg: riskVerifyRes.message
            }
        } else {
            // 其他错误
            Debug(riskVerifyRes.message);
            return {
                code: 4,
                msg: riskVerifyRes.message
            }
        }
    } else {
        return {
            ...riskVerifyRes,
            code: 0,
            msg: riskVerifyRes.message
        }
    }
}

// 二验提交验证码
async function risk_verify_code(account, code) {
    try {
        let body = request({
            url: `${acUrl}/bot/risk/risk_verify_code?BotApiToken=${botApiToken}`,
            method: "post",
            body: {
                account,
                code
            },
            timeOut: 30000,
        })
        Debug(body)
        let res = JSON.parse(body);
        return res
    } catch (error) {
        notifyMasters(`账号${account}二验验证码请求失败:${error}`)
        return { success: false, message: error.message };
    }
}

// 二验图形验证码
async function risk_auto_captcha(account) {
    try {
        let body = request({
            url: `${acUrl}/bot/risk/risk_send?BotApiToken=${botApiToken}`,
            method: "post",
            body: {
                account
            },
            timeOut: 30000,
        })
        Debug(body)
        let res = JSON.parse(body);
        return res
    } catch (error) {
        notifyMasters(`账号${account}二验图形验证失败:${error}`)
        return { success: false, message: error.message };
    }
}

// 二验获取状态
async function risk_send(account) {
    try {
        let body = request({
            url: `${acUrl}/bot/risk/risk_send?BotApiToken=${botApiToken}`,
            method: "post",
            body: {
                account
            },
            timeOut: 30000,
        })
        Debug(body)
        let res = JSON.parse(body);
        return res
    } catch (error) {
        notifyMasters(`账号${account}二验获取状态失败:${error}`)
        return { success: false, message: error.message };
    }
}

// 初始化函数
async function init(account) {
    try {
        if (!account) {
            return { success: false, code: 505, message: "账号不能为空" };
        }

        let body = request({
            url: `${acUrl}/bot/pwd/init?BotApiToken=${botApiToken}`,
            method: "post",
            body: {
                account
            },
            timeOut: 30000,
        });

        if (!body) {
            return { success: false, code: 505, message: "API返回为空" };
        }

        Debug(`init接口返回: ${body}`);
        let res = JSON.parse(body);
        return res;
    } catch (error) {
        Debug(`init请求失败: ${error.message}`);
        return {
            success: false,
            code: 505,
            message: `初始化失败: ${error.message}`
        };
    }
}

// 自动验证码处理
async function autoCaptcha(account) {
    try {
        let body = request({
            url: `${acUrl}/bot/pwd/auto_captcha?BotApiToken=${botApiToken}`,
            method: "post",
            body: {
                account
            },
            timeOut: 30000,
        })
        Debug(body)
        let res = JSON.parse(body);
        return res
    } catch (error) {
        notifyMasters(`账号${account}账密登录验证码请求失败:${error}`)
        return { success: false, message: error.message };
    }
}

async function login(account, pwd) {
    try {
        if (!account || !pwd) {
            return {
                success: false,
                code: 505,
                message: "账号或密码不能为空"
            };
        }

        let encryptedPwd = encrypt_pwd_aes_gcm(pwd, account);
        let body = request({
            url: `${acUrl}/bot/pwd/login?BotApiToken=${botApiToken}`,
            method: "post",
            body: {
                account,
                pwd: encryptedPwd
            },
            timeOut: 30000,
        });

        if (!body) {
            return {
                success: false,
                code: 505,
                message: "API返回为空"
            };
        }

        Debug(`login接口返回: ${body}`);
        let res = JSON.parse(body);
        return res;
    } catch (error) {
        Debug(`login请求失败: ${error.message}`);
        return {
            success: false,
            code: 505,
            message: `登录失败: ${error.message}`
        };
    }
}

function addRetry(account, password, user, platform) {
    let ranks = JSON.parse(bucketGet(actongzi, "ranks") || '[]');
    // 清理超过30分钟的记录
    ranks = ranks.filter(item => !isMoreThanHalfHourLater(item.time, getCurrentTime()));

    // 添加新的重试记录
    ranks.push({
        account,
        platform,
        time: getCurrentTime(),
        retryCount: 1
    });

    bucketSet(actongzi, "ranks", JSON.stringify(ranks));

    // 设置延时重试
    ShuRu(120000)
    doLogin(account, password, user, platform);
}

function clearQueue(account) {
    let ranks = JSON.parse(bucketGet(actongzi, "ranks") || '[]');
    let index = ranks.findIndex(item => item.account === account);
    if (index !== -1) {
        ranks.splice(index, 1);
    }
    bucketSet(actongzi, "ranks", JSON.stringify(ranks));
}

function getPinByCk(ck) {
    if (!ck) sendText(`未获取到ck`);

    const match = ck.match(/(?<=(pt_pin|pin)=).*?(?=;|$)/);
    if (match) {
        return match[0];
    }
    sendText(`未获取到pin ${ck}`);
}

function ShuRu(timeout = 60000) {
    var msg = input(timeout, 1000)
    if (!msg) {
        sendText(`${timeout / 1000}秒内未回复，已退出会话。`)
        return false
    } else if (msg == "q" || msg == "Q") {
        sendText("已退出会话");
        return false
    } else {
        return msg;
    }
}

function handleLoginFailure(account) {
    const failedLoginThreshold = parseInt(bucketGet(actongzi, 'failedLoginThreshold') || '0');
    let loginFailures = JSON.parse(bucketGet(actongzi, 'loginFailures') || '{}');

    if (!loginFailures[account]) {
        loginFailures[account] = 0;
    }

    loginFailures[account]++;

    bucketSet(actongzi, 'loginFailures', JSON.stringify(loginFailures));

    // 当 failedLoginThreshold 为 0 时，不删除失效账号
    if (failedLoginThreshold > 0 && loginFailures[account] >= failedLoginThreshold) {
        const keys = bucketKeys(actongzi);
        for (const pin of keys) {
            const record = bucketGet(actongzi, pin);
            if (record && record.indexOf("password") !== -1) {
                try {
                    const parsedRecord = JSON.parse(record);
                    if (parsedRecord.account === account) {
                        bucketDel(actongzi, pin);
                        delete loginFailures[account];
                        bucketSet(actongzi, 'loginFailures', JSON.stringify(loginFailures));
                        push({
                            imType: platform,
                            userID: user,
                            content: `账号${account}登录失败达到${failedLoginThreshold}次，已自动删除桶数据`,
                        });
                        notifyMasters(`账号${account}因登录失败次数过多，已自动删除桶数据`);
                        break;
                    }
                } catch (e) {
                    Debug(`解析记录失败: ${e.message}`);
                }
            }
        }
    }
}

function resetLoginFailureCount(account) {
    let loginFailures = JSON.parse(bucketGet(actongzi, 'loginFailures') || '{}');
    if (loginFailures[account]) {
        delete loginFailures[account];
        bucketSet(actongzi, 'loginFailures', JSON.stringify(loginFailures));
    }
}

AccountMain()
