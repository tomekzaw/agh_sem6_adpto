#include <iostream>
#include <queue>
#include <tuple>
#include <map>
#include <vector>
#include <algorithm>

using namespace std;

typedef map<int, vector<int>> graph;
typedef map<int, tuple<int, int, int>> foldmem;

inline int index(int y, int x, int W) {
    return y*W + x;
}

inline bool has(const vector<int>& vec, const int& elem) {
    return find(vec.begin(), vec.end(), elem) != vec.end();
}

inline void remove(vector<int>& vec, const int& elem) {
    vec.erase(remove(vec.begin(), vec.end(), elem), vec.end());
}

inline void add(vector<int>& vec, const int& elem) {
    if (!has(vec, elem)) {
        vec.push_back(elem);
    }
}

graph create_graph(char* board, int W, int H, int L) {
    int* visited = new int[W*H];
    for (int i = 0; i < W*H; ++i) {
        visited[i] = -1;
    }

    graph G;
    for (int y = 0; y < H; ++y) {
        for (int x = 0; x < W; ++x) {
            int idx = index(y, x, W);

            if (board[idx] == '.') {
                continue;
            }

            queue<tuple<int, int, int>> q = queue<tuple<int, int, int>>();
            q.push(tuple<int, int, int>(y, x, L));

            while (!q.empty()) {
                tuple<int, int, int> t = q.front();
                q.pop();

                int d = get<2>(t);
                if (d <= 0) {
                    continue;
                }

                int y = get<0>(t), x = get<1>(t);
                int idx2 = index(y, x, W);
                char curr = board[idx2];

                if (curr == '+' || curr == '|') {
                    if (y > 0) {
                        int idx3 = index(y-1, x, W);
                        if (visited[idx3] != idx) {
                            char up = board[idx3];
                            if (up == '+' || up == '|') {
                                add(G[idx], idx3);
                                visited[idx3] = idx;
                                q.push(tuple<int, int, int>(y-1, x, d-1));
                            }
                        }
                    }
                    if (y < H-1) {
                        int idx3 = index(y+1, x, W);
                        if (visited[idx3] != idx) {
                            char down = board[idx3];
                            if (down == '+' || down == '|') {
                                add(G[idx], idx3);
                                visited[idx3] = idx;
                                q.push(tuple<int, int, int>(y+1, x, d-1));
                            }
                        }
                    }
                }
                if (curr == '+' || curr == '-') {
                    if (x > 0) {
                        int idx3 = index(y, x-1, W);
                        if (visited[idx3] != idx) {
                            char left = board[idx3];
                            if (left == '+' || left == '-') {
                                add(G[idx], idx3);
                                visited[idx3] = idx;
                                q.push(tuple<int, int, int>(y, x-1, d-1));
                            }
                        }
                    }
                    if (x < W-1) {
                        int idx3 = index(y, x+1, W);
                        if (visited[idx3] != idx) {
                            char right = board[idx3];
                            if (right == '+' || right == '-') {
                                add(G[idx], idx3);
                                visited[idx3] = idx;
                                q.push(tuple<int, int, int>(y, x+1, d-1));
                            }
                        }
                    }
                }
            }

            remove(G[idx], idx); // don't include node in its neighbour list
        }
    }

    delete[] visited;

    return G;
}

void debug_print_graph(graph& G, const int W) {
    for (auto& entry : G) {
        int idx = get<0>(entry);
        vector<int>& neighbours = get<1>(entry);
        cout << idx << ": ";
        for (int idx2 : neighbours) {
            cout << idx2 << ' ';
        }
        cout << endl;
    }
}

graph extract_single_component(graph& G, int W, int H) {
    if (G.empty()) {
        return G;
    }

    graph C;
    bool* visited = new bool[W*H]{false};

    int any = get<0>(*G.begin());
    queue<int> q;
    visited[any] = true;
    q.push(any);

    while (!q.empty()) {
        int v = q.front();
        q.pop();

        for (int n : G[v]) {
            if (!visited[n]) {
                visited[n] = true;
                q.push(n);
            }
        }

        C[v] = vector<int>(G[v]);
        G.erase(v);
    }

    delete[] visited;
    return C;
}

void remove_isolates(graph& G, int W, int& K) {
    for (auto it = G.cbegin(); it != G.cend(); ) {
        vector<int> neighbours = get<1>(*it);
        if (neighbours.empty()) {
            int idx = get<0>(*it);
            int y = idx / W, x = idx % W;
            cout << x << ' ' << y << endl;
            if (!--K) {
                exit(0);
            }
            G.erase(it++);
        } else {
            ++it;
        }
    }
}

int difficulty(const graph& G) {
    int v = G.size();
    int e = 0;
    for (auto entry : G) {
        vector<int>& neigh = get<1>(entry);
        e += neigh.size();
    }
    return e;
}

inline bool independent_set_recursive(graph& G, int K, vector<int>& I, foldmem& mem) {
    static int lastz = -1;

    start:

    if (K == 0) {
        for (auto& entry : mem) {
            int z = get<0>(entry);
            tuple<int, int, int>& vuw = get<1>(entry);
            int v = get<0>(vuw), u = get<1>(vuw), w = get<2>(vuw);

            if (has(I, z)) {
                remove(I, z);
                add(I, u);
                add(I, w);
            } else {
                add(I, v);
            }
        }

        return true;
    }

    if (G.empty()) {
        return false;
    }

    int u, deg_u = 299792458;
    for (auto& entry : G) {
        int v = get<0>(entry);

        vector<int>& neigh = get<1>(entry);
        int deg_v = neigh.size();

        // deg 0
        if (deg_v == 0) {
            G.erase(v);
            add(I, v);
            --K;
            goto start;
        }

        // deg 1
        if (deg_v == 1) {
            int a = G[v][0];
            for (int b : G[a]) {
                remove(G[b], a);
            }
            G.erase(a);
            G.erase(v);
            add(I, v);
            --K;
            goto start;
        }

        // deg 2
        if (deg_v == 2) {
            int u = G[v][0], w = G[v][1];

            if (has(G[u], w)) { // uw in E
                for (int a : G[v]) {
                    for (int b : G[a]) {
                        if (b != v) {
                            remove(G[b], a);
                        }
                    }
                    G.erase(a);
                }
                G.erase(v);
                add(I, v);
                --K;
                goto start;
            } else { // uw not in E
                int z = --lastz;
                foldmem mem2(mem);
                mem2[z] = tuple<int, int, int>(v, u, w);

                G[z] = vector<int>();

                for (int n : G[u]) {
                    if (n != v) {
                        add(G[z], n);
                        add(G[n], z);
                        remove(G[n], u);
                    }
                }
                for (int n : G[w]) {
                    if (n != v) {
                        add(G[z], n);
                        add(G[n], z);
                        remove(G[n], w);
                    }
                }

                G.erase(v);
                G.erase(u);
                G.erase(w);

                return independent_set_recursive(G, K-1, I, mem2);
            }
        }

        // find min deg
        if (deg_v < deg_u) {
            deg_u = deg_v;
            u = v;
        }
    }

    // left branch
    graph G1(G);
    vector<int> I1(I);

    for (int v : G1[u]) {
        for (int w : G1[v]) {
            if (w != u) {
                remove(G1[w], v);
            }
        }
        G1.erase(v);
    }
    G1.erase(u);
    add(I, u);

    if (independent_set_recursive(G1, K-1, I, mem)) {
        return true;
    }

    I = I1;

    // right branch
    for (int v : G[u]) {
        remove(G[v], u);
    }
    G.erase(u);

    return independent_set_recursive(G, K, I, mem);
}

vector<int> independent_set(graph& G, int K) {
    vector<int> I;
    foldmem mem;
    independent_set_recursive(G, K, I, mem);
    return I;
}

int MIS_size(graph& G) {
    int bonus = 0;

    start:

    if (G.empty()) {
        return bonus;
    }

    int u, deg_u = -1;

    for (auto entry : G) {
        int v = get<0>(entry);
        vector<int> neigh = get<1>(entry);
        int deg_v = neigh.size();

        if (deg_v == 0) {
            G.erase(v);
            ++bonus;
            goto start;
        }

        if (deg_v == 1) {
            int w = G[v][0];
            for (int n : G[w]) {
                remove(G[n], w);
            }
            G.erase(w);
            G.erase(v);
            ++bonus;
            goto start;
        }

        if (deg_v > deg_u) {
            u = v;
            deg_u = deg_v;
        }
    }

    // u has max deg

    graph G2(G);

    for (int v : G[u]) {
        for (int w : G[v]) {
            if (w != u) {
                remove(G[w], v);
            }
        }
        G.erase(v);
    }
    G.erase(u);

    int alpha1 = 1 + MIS_size(G);

    for (int v : G2[u]) {
        remove(G2[v], u);
    }
    G2.erase(u);

    int alpha2 = MIS_size(G2);

    return bonus + max(alpha1, alpha2);
}

int main() {
    int W, H, L, K;
    cin >> W >> H >> L >> K;

    string name;
    cin >> name;

    char* board = new char[H*W+1];
    for (int y = 0; y < H; ++y) {
        cin >> board + y*W;
    }

    if (K == 0) {
        return 0;
    }

    if (L == 0) {
        for (int y = 0; y < H; ++y) {
            for (int x = 0; x < W; ++x) {
                if (board[index(y, x, W)] != '.') {
                    cout << x << ' ' << y << endl;
                    if (!--K) {
                        return 0;
                    }
                }
            }
        }
    }

    graph G = create_graph(board, W, H, L);

    remove_isolates(G, W, K);

    vector<graph> components;
    while (true) {
        graph C = extract_single_component(G, W, H);
        if (C.empty()) {
            break;
        }
        components.push_back(C);
    }

    // sort components by size
    sort(components.begin(), components.end(), [](const graph& a, const graph& b){ return difficulty(a) < difficulty(b); });

    graph last_C = components.back();
    components.pop_back();

    for (graph C : components) {
        graph C_copy(C);
        int alpha = MIS_size(C_copy);
        vector<int> I = independent_set(C, alpha);

        K -= alpha;

        for (auto idx : I) {
            int y = idx / W, x = idx % W;
            cout << x << ' ' << y << endl;
        }
    }

    vector<int> I = independent_set(G, K);

    for (auto idx : I) {
        int y = idx / W, x = idx % W;
        cout << x << ' ' << y << endl;
    }

    return 0;
}
