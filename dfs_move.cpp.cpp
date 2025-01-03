#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <set>
#include <vector>
#include <list>
#include <unordered_map>
#include <map>
#include <memory>
#include <functional>
#include <algorithm>
#include <cmath>
#include <chrono>

using namespace std;

typedef pair<int, int> x_and_y_t;
typedef multiset<int> erased_block_sets_t;

const int BLOCK_NUM = 140;
const int block_h_line = 10;
const int block_v_line = 14;
const int direc_length = 4;
const int total_count = 70;

const int direcs[direc_length]  = { 0,1,2,3 };
const char symbol[direc_length] = { '^','v','<','>' };
int opposite_direcs[direc_length] = { 1, 0, 3, 2 };
int nsteps[BLOCK_NUM] = { 0 };
int ndirecs[BLOCK_NUM] = { 0 };

bool stop_flag = false;

int cut_count = 0;
int cache_count = 0;

auto start = std::chrono::high_resolution_clock::now();

void show_time_eclipse(){
	auto end = std::chrono::high_resolution_clock::now();
	std::chrono::duration<double> elapsed = end - start;
	std::cout << "Elapsed time: " << elapsed.count() << " seconds" << std::endl;
}

string block_map_path = R"(C:\Users\Administrator\Desktop\block_map.csv)";
string operation_path = R"(C:\Users\Administrator\Desktop\oplist.csv)";

struct block_map_t {
	int block_poss[BLOCK_NUM];
	
	block_map_t() {
		memset(block_poss, -1, sizeof(block_poss));
	}

	int loc(int y, int x) {
		return  block_poss[y * block_h_line + x];
	}

	void set(int y, int x, int v) {
		block_poss[y * block_h_line + x] = v;
	}
};

block_map_t block_map;
vector<shared_ptr<block_map_t>> block_map_valid;
vector<shared_ptr<block_map_t>> block_map_invalid;

unordered_map<int,set<x_and_y_t>> block_id_loc_sets;

struct block_map_snapshot_t {
	erased_block_sets_t erased_blocks;
	int df_values[BLOCK_NUM];

	block_map_snapshot_t(erased_block_sets_t& _erased_blocks, block_map_t& _block_map)//:erased_blocks(_erased_blocks)
	{
		memcpy(&df_values, &_block_map.block_poss,sizeof(df_values));
		cache_count++;
	}
};

struct base_operation{
	int op_type;
	int x = x;
	int y = y;
	base_operation(int _op_type, int _x, int _y ):op_type(_op_type), x(_x), y(_y) {}

	virtual ~base_operation() {}
};

struct elmination:public base_operation{
	int block_id = block_id;

	elmination(int _x,int _y,int _block_id):base_operation(0, _x, _y), block_id(_block_id) {}
};

struct movement:public base_operation{
	int step;
	int _dir;

	movement(int _x, int _y, int _step, int __dir):base_operation(1, _x, _y), step(_step), _dir(__dir) {}
};

class operations {
public:
	list<shared_ptr<base_operation>> op_list;

	void add_elmination(int x, int y, int block_id) {
		shared_ptr<base_operation> el = make_shared<elmination>(x, y, block_id);
		op_list.emplace_back(el);
	}

	void add_movement(int x, int y, int step, int _dir) {
		shared_ptr<base_operation> el = make_shared<movement>(x, y, step, _dir);
		op_list.emplace_back(el);
	}

	void pop_back(int n = 1) {
		for (int i = 0; i < n; i++)
			op_list.pop_back();
	}
};

auto ops = operations();

struct PairHash {
	size_t operator()(const std::pair<int, int>& p) const {
		return std::hash<int>()(p.first) ^ std::hash<int>()(p.second);
	}
};

unordered_map<x_and_y_t, vector<block_map_snapshot_t>, PairHash> cache_map;

inline bool is_valid(int v) {
	return v != -1;
};

inline bool not_valid(int v) {
	return v == -1;
};

inline void disappear(int x, int y) {
	cout << "disappear :" << y << ' ' << x << endl;
	block_map.set(y, x, -1);
}

inline void redisappear(int x, int y, int block_id) {
	cout << "disappear :" << y << ' ' << x << endl;
	block_map.set(y, x, block_id);
}

inline bool _is_same(int x, int y, int _x, int _y) {
	if (_x != -1 && _y != -1 && x != -1 && y != -1)
		return block_map.loc(y, x) == block_map.loc(_y, _x);
	else
		return false;
}

auto inline xy_transform(int x, int y, int _dir, int step){
	if (_dir == 0)
		return x_and_y_t(x, y - step);
	else if (_dir == 1)
		return x_and_y_t(x, y + step);
	else if (_dir == 2)
		return x_and_y_t(x - step, y);
	else if (_dir == 3)
		return x_and_y_t(x + step, y);
}

template<class T>
x_and_y_t first_valid_or_invalid(int x, int y, int _dir, T& f) {
	if (_dir == 0) {
		for (int i = y - 1; i >= 0; i--) {
			if (f(block_map.loc(i, x)))
				return x_and_y_t(x, i);
		}
	}
	else if (_dir == 1) {
		for (int i = y + 1; i < block_v_line; i++) {
			if (f(block_map.loc(i, x)))
				return x_and_y_t(x, i);
		}
	}
	else if (_dir == 2) {
		for (int i = x - 1; i >= 0; i--) {
			if (f(block_map.loc(y, i)))
				return x_and_y_t(i, y);
		}
	}
	else if (_dir == 3) {
		for (int i = x + 1; i < block_h_line; i++) {
			if (f(block_map.loc(y, i)))
				return x_and_y_t(i, y);
		}
	}
	return x_and_y_t(-1, -1);
}

x_and_y_t valid_fast_return(int x_or_y, int x, int y, int _dir) {
	if (x_or_y == -1) {
		return x_and_y_t(-1, -1);
	}
	if (_dir > 1)
		return x_and_y_t(x_or_y, y);
	else return x_and_y_t(x, x_or_y);
}

x_and_y_t first_valid(int x, int y, int _dir, bool init = false) {
	if (init == true) {
		auto ret = first_valid_or_invalid(x, y, _dir, is_valid);
		return ret;
	}
	else {
		int x_or_y = block_map_valid[_dir]->loc(y, x);
		return valid_fast_return(x_or_y, x, y, _dir);
	}
}

x_and_y_t first_invalid(int x, int y, int _dir, bool init = false) {
	if (init == true) {
		auto ret = first_valid_or_invalid(x, y, _dir, not_valid);
		return ret;
	}
	else {
		int x_or_y = block_map_invalid[_dir]->loc(y, x);
		return valid_fast_return(x_or_y, x, y, _dir);
	}
}

x_and_y_t last_invalid(int x, int y, int _dir) {
	auto ret = first_valid(x, y, _dir);
	return ret;
}

x_and_y_t last_valid(int x, int y, int _dir) {
	auto ret = first_invalid(x, y, _dir);
	return ret;
}

int find_max_step(int x, int y, int _dir) {

	auto _pos = first_invalid(x, y, _dir);
	int _x = _pos.first;
	int _y = _pos.second;
	if (_x == -1 || _y == -1) {
		return 0;
	}
	
	auto _pos2 = last_invalid(_x, _y, _dir);
	int _x1 = _pos2.first;
	int _y1 = _pos2.second;

	if (_dir == 0) {
		if (_y1 == -1)
			return _y + 1;
		else
			return _y - _y1;
	}
	if (_dir == 1) {
		if (_y1 == -1)
			return block_v_line - _y;
		else
			return _y1 - _y;
	}
	if (_dir == 2) {
		if (_x1 == -1)
			return _x + 1;
		else
			return _x - _x1;
	}
	if (_dir == 3) {
		if (_x1 == -1)
			return block_h_line - _x;
		else
			return _x1 - _x;
	}
	return 0;
}

inline bool _not(bool x) {
	return !x;
}

inline bool _yes(bool x) {
	return x;
}

vector<function<bool(int)>> _id_valid_dp  = { is_valid, not_valid };
vector<function<bool(bool)>> _judge_dp{ _yes,_not };
int zip_num_dp = 2;

void update_valid_and_invalid_map_disappear_or_redisappear(int x, int y, bool _disappear) {

	int _dir = 0;
	for (int idx = 0; idx < zip_num_dp; idx++) {
		auto& iblock_map = ( idx == 0 ) ? block_map_valid : block_map_invalid;
		auto tblock = iblock_map[_dir];

		auto ifunc = _id_valid_dp[idx];
		auto ilogic = _judge_dp[idx];
		
		for (int i = y + 1; i < block_v_line; i++) {
			tblock->set(i, x, ilogic(_disappear) ? tblock->loc(i - 1, x) : y);
			if (ifunc(block_map.loc(i, x)))
				break;
		}
	}

	_dir = 1;
	for (int idx = 0; idx < zip_num_dp; idx++) {
		auto& iblock_map = (idx == 0) ? block_map_valid : block_map_invalid;
		auto tblock = iblock_map[_dir];

		auto ifunc = _id_valid_dp[idx];
		auto ilogic = _judge_dp[idx];

		for (int i = y - 1; i >= 0; i--) {
			tblock->set(i, x, ilogic(_disappear) ? tblock->loc(i + 1, x) : y);
			if (ifunc(block_map.loc(i, x)))
				break;
		}
	}

	_dir = 2;
	for (int idx = 0; idx < zip_num_dp; idx++) {
		auto& iblock_map = (idx == 0) ? block_map_valid : block_map_invalid;
		auto tblock = iblock_map[_dir];

		auto ifunc = _id_valid_dp[idx];
		auto ilogic = _judge_dp[idx];

		for (int i = x + 1; i < block_h_line; i++) {
			tblock->set(y, i, ilogic(_disappear) ? tblock->loc(y, i-1) : x);
			if (ifunc(block_map.loc(y, i)))
				break;
		}
	}

	_dir = 3;
	for (int idx = 0; idx < zip_num_dp; idx++) {
		auto& iblock_map = (idx == 0) ? block_map_valid : block_map_invalid;
		auto tblock = iblock_map[_dir];

		auto ifunc = _id_valid_dp[idx];
		auto ilogic = _judge_dp[idx];

		for (int i = x - 1; i >= 0; i--) {
			tblock->set(y, i, ilogic(_disappear) ? tblock->loc(y, i + 1) : x);
			if (ifunc(block_map.loc(y, i)))
				break;
		}
	}
}

inline void update_valid_and_invalid_map_disappear(int x, int y) {
	update_valid_and_invalid_map_disappear_or_redisappear(x, y, true);
}

inline void update_valid_and_invalid_map_redisappear(int x, int y) {
	update_valid_and_invalid_map_disappear_or_redisappear(x, y, false);
}

void dump_opreations() {
	std::ofstream file(operation_path);
	if (!file) {
		std::cerr << "can not open file!" << std::endl;
		exit(-1);
	}

	for (shared_ptr<base_operation> op : ops.op_list) {
		file << op->op_type << ',' << op->y << ',' << op->x << ',';
		if (op->op_type == 0) {
			file << std::dynamic_pointer_cast<elmination>(op)->block_id << ',' << 0 << endl;
		}
		else {
			file << std::dynamic_pointer_cast<movement>(op)->step << ',' << std::dynamic_pointer_cast<movement>(op)->_dir  << endl;
		}
	}
	file.close();
}

void record_this_graph( int move_count_all,int block_id_count, multiset<int>& erased_blocks) {
	vector<block_map_snapshot_t>& _icache = cache_map[x_and_y_t(move_count_all, block_id_count)];
	_icache.emplace_back(block_map_snapshot_t(erased_blocks, block_map));
}

bool has_occured(int move_count_all, int block_id_count, multiset<int>& erased_blocks) {
	
	if (cache_map.find(x_and_y_t(move_count_all, block_id_count)) == cache_map.end()) {
		cache_map[x_and_y_t(move_count_all, block_id_count)] = vector<block_map_snapshot_t>();
		return false;
	}
	else {
		auto& caches = cache_map[x_and_y_t(move_count_all, block_id_count)];
		for (auto& icache : caches) {
			/*if (icache.erased_blocks.size() == erased_blocks.size()) {
				if (icache.erased_blocks == erased_blocks) {
					for (int i = 0; i < BLOCK_NUM; i++) {
						if (icache.df_values[i] != block_map.block_poss[i]) {
							return false;
						}
					}
					cut_count += 1;
					return true;
				}
			}*/
			if (memcmp(icache.df_values, block_map.block_poss, sizeof(block_map.block_poss)) == 0) {
				cut_count += 1;
				return true;
			}
		}
	}
	return false;
}

int move_cache[BLOCK_NUM] = { 0 };
x_and_y_t _move(int x,int y,int step, int _dir) {
	auto _p = last_valid(x, y, _dir);
	int _x = _p.first;
	int _y = _p.second;
		
	int erase_len = abs(_y - y) + abs(_x - x);
	for (int i = 0; i < erase_len; i++) {
		auto tt = xy_transform(x, y, _dir, i);
		move_cache[i] = block_map.loc(tt.second, tt.first);
		block_id_loc_sets[block_map.loc(tt.second, tt.first)].erase(tt);
		block_map.set(tt.second, tt.first, -1);
		update_valid_and_invalid_map_disappear(tt.first, tt.second);
	}

	for (int i = 0; i < erase_len; i++) {
		auto tt = xy_transform(x, y, _dir, i + step);
		block_map.set(tt.second, tt.first, move_cache[i]);
		block_id_loc_sets[block_map.loc(tt.second, tt.first)].insert(tt);
		update_valid_and_invalid_map_redisappear(tt.first, tt.second);
	}

	return xy_transform(_x, _y, _dir, step - 1);
}

void show_block_map(shared_ptr<block_map_t> _block_map) {
	for (int y = 0; y < block_v_line; y++) {
		for (int x = 0; x < block_h_line; x++) {
			cout << _block_map->loc(y, x) << ' ';
		}
		cout << endl;
	}
}

void show_block_map(block_map_t* _block_map) {
	for (int y = 0; y < block_v_line; y++) {
		for (int x = 0; x < block_h_line; x++) {
			cout << _block_map->loc(y, x) << ' ';
		}
		cout << endl;
	}
}

void show_all_dp_block_map() {
	///show
	for (int i = 0; i < direc_length; i++) {
		show_block_map(block_map_valid[i]);
		cout << endl;
		show_block_map(block_map_invalid[i]);
		cout << endl;
	}
}

bool dfs(int move_count_all, int block_id_count, erased_block_sets_t& erased_blocks);

bool try_move(int x, int y, int _dir, int move_count_all, int block_id_count, erased_block_sets_t& erased_blocks) {
	auto _class = block_map.loc(y, x);
	auto block_id = block_map.loc(y, x);

	x_and_y_t pos = first_valid(x, y, _dir);
	int _x = pos.first;
	int _y = pos.second;
	
	if (_is_same(x, y, _x, _y)) {
		cout << "( " << y << ',' << x << " ) " << "( " << _y << ',' << _x << " ) " << endl;
		///i
		disappear(x, y);
		block_id_loc_sets[_class].erase(x_and_y_t(x, y));
		update_valid_and_invalid_map_disappear(x, y);
		///ii
		disappear(_x, _y);
		block_id_loc_sets[_class].erase(x_and_y_t(_x, _y));
		update_valid_and_invalid_map_disappear(_x, _y);
		///iii
		ops.add_elmination(x, y, block_id);
		ops.add_elmination(_x, _y, block_id);
		///iiii
		erased_blocks.insert(block_id);

		//show_all_dp_block_map();

		if (!has_occured(move_count_all + 1, block_id_count + block_id, erased_blocks) && !stop_flag) {
			record_this_graph(move_count_all + 1, block_id_count + block_id, erased_blocks);
			dfs(move_count_all + 1, block_id_count + block_id, erased_blocks);
		}

		///iiii
		erased_blocks.erase(block_id);
		///iii
		ops.pop_back(2);
		///ii
		redisappear(_x, _y, block_id);
		block_id_loc_sets[_class].insert(x_and_y_t(_x, _y));
		update_valid_and_invalid_map_redisappear(_x, _y);
		///i
		redisappear(x, y, block_id);
		block_id_loc_sets[_class].insert(x_and_y_t(x, y));
		update_valid_and_invalid_map_redisappear(x, y);

		return true;
	}

	///algo search v & h line
	int	max_step = find_max_step(x, y, _dir);

	if (max_step == 0)
		return false;

	///algo map match
	int to_be_matched = 0;
	for (auto& _p : block_id_loc_sets[_class]) {
		int _x = _p.first;
		int _y = _p.second;

		if ((_x != x) && (_y != y)) {
			int dx = x - _x;
			int	dy = y - _y;
			int find_direc_x = dx > 0 ? 2 : 3;
			int	find_direc_y = dy > 0 ? 0 : 1;

			if (_dir < 2 && (_dir == find_direc_y) && (dx != 0) && (0 < abs(dy)) && (abs(dy) <= max_step)) {
				nsteps[to_be_matched] = abs(dy);
				ndirecs[to_be_matched++] = find_direc_x;
			}

			else if (_dir > 1 && (_dir == find_direc_x) && (dy != 0) && (0 < abs(dx)) && (abs(dx) <= max_step)) {
				nsteps[to_be_matched] = abs(dx);
				ndirecs[to_be_matched++] = find_direc_y;
			}
		}
	}

	cout << "max_step = " << max_step << " to_be_matched = " << to_be_matched << endl;

	for (int ii = 0; ii < to_be_matched; ii++) {
		auto i = nsteps[ii];
		auto _d = ndirecs[ii];
		cout << "step_direc_zip = " << symbol[_dir] << ' ' << i << ' ' << symbol[_d] << endl;

		///move to(xt, yt)
		x_and_y_t  __xy0 = xy_transform(x, y, _dir, i);
		auto xt = __xy0.first;
		auto yt = __xy0.second;
		///match(_x, _y)
		x_and_y_t  __xy1 = first_valid(xt, yt, _d);
		auto _x = __xy1.first;
		auto _y = __xy1.second;		 

		if (_is_same(x, y, _x, _y)) {
			///move and disappear
			///0
			x_and_y_t  __xy2 = _move(x, y, i, _dir);
			auto xh = __xy2.first;
			auto yh = __xy2.second;
			///i
			disappear(_x, _y);
			block_id_loc_sets[_class].erase(x_and_y_t(_x, _y));
			update_valid_and_invalid_map_disappear(_x, _y);
			///ii
			disappear(xt, yt);
			block_id_loc_sets[_class].erase(x_and_y_t(xt, yt));
			update_valid_and_invalid_map_disappear(xt, yt);
			///iii
			ops.add_movement(x, y, i, _dir);
			ops.add_elmination(_x, _y, block_id);
			///iV
			erased_blocks.erase(block_id);
					
			if (!has_occured(move_count_all + 1, block_id_count + block_id, erased_blocks) && !stop_flag) {
				record_this_graph(move_count_all + 1, block_id_count + block_id, erased_blocks);
				dfs(move_count_all + 1, block_id_count + block_id, erased_blocks);
			}

			///
			erased_blocks.insert(block_id);
			///i
			ops.pop_back(2);
			///ii
			redisappear(xt, yt, block_id);
			block_id_loc_sets[_class].insert(x_and_y_t(xt, yt));
			update_valid_and_invalid_map_redisappear(xt, yt);
			///iii
			redisappear(_x, _y, block_id);
			block_id_loc_sets[_class].insert(x_and_y_t(_x, _y));
			update_valid_and_invalid_map_redisappear(_x, _y);
			///0
			_move(xh, yh, i, opposite_direcs[_dir]);

			return true;
		}
	}
	return true;
}

bool dfs(int move_count_all, int block_id_count, erased_block_sets_t& erased_blocks)
{	
	cout << "move_count_all = " << move_count_all << endl;

	if (stop_flag == true)
		return true;

	if (move_count_all == total_count) {
		stop_flag = true;
		cout << "solution path found" << endl;
		dump_opreations();
		//show_block_map(&block_map);
		show_time_eclipse();
		exit(0);
		return true;
	}

	for (int x = 0; x < block_h_line; x++) {
		for (int y = 0; y < block_v_line; y++) {
			if(block_map.loc(y, x) != -1){
				for (int _dir = 0; _dir < direc_length; _dir++) {
					printf("search y = %d, x = %d, dir = %c, count = %d, cache_graphs = %d, cut_count = %d\n", y, x, symbol[_dir], move_count_all, cache_count, cut_count);
					try_move(x, y, _dir, move_count_all, block_id_count, erased_blocks);
				}
				cout << "-------------------------------------" << endl;
			}
		}
	}

	return false;
}

inline int get_x_or_y_depend_on(x_and_y_t& _pos, int _dir) {
	return _dir < 2 ? _pos.second : _pos.first;
}

void create_block_map() {
	std::ifstream file(block_map_path);
	if (!file) {
		std::cerr << "can not open file!" << std::endl;
		exit(-1);
	}

	std::string line;
	int y = 0;
	std::getline(file, line);
	while (std::getline(file, line)) {
		std::stringstream ss(line);
		std::string cell;
		int x = 0;
		std::getline(ss, cell, ',');
		while (std::getline(ss, cell, ',')) {
			block_map.set(y, x, atoi(cell.c_str()));
			x++;
		}
		y++;
	}
	file.close();

	for (int x = 0; x < block_h_line; x++) {
		for (int y = 0; y < block_v_line; y++) {
			int _type = block_map.loc(y, x);
			block_id_loc_sets[_type].insert(x_and_y_t(x,y));
		}
	}

	for (int i = 0; i < direc_length; i++) {
		{
			auto iblock = make_shared<block_map_t>();
			block_map_valid.emplace_back(iblock);
		}
		{
			auto iblock = make_shared<block_map_t>();
			block_map_invalid.emplace_back(iblock);
		}
	}

	for (int x = 0; x < block_h_line; x++) {
		for (int y = 0; y < block_v_line; y++) {
			for (int _dir = 0; _dir < direc_length; _dir++) {
				{
					x_and_y_t _pos = first_valid(x, y, _dir, true);
					block_map_valid[_dir]->set(y, x, get_x_or_y_depend_on(_pos, _dir));
				}
				{
					x_and_y_t _pos = first_invalid(x, y, _dir, true);
					block_map_invalid[_dir]->set(y, x, get_x_or_y_depend_on(_pos, _dir));
				}
			}
		}
	}
}

int main()
{
	create_block_map();
	auto erased_blocks = erased_block_sets_t();
	dfs(0, 0, erased_blocks);
	if (!stop_flag) {
		cout << "No Solution" << endl;
	}
	else {
		cout << "found" << endl;
	}
	show_time_eclipse();
	return 0;
}

