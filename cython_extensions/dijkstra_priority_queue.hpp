#include <functional>
#include <queue>
#include <utility>

using coords = std::pair<int,int>;
using item = std::pair<double,coords>;
using cpp_pq = std::priority_queue<item,std::vector<item>,std::function<bool(item,item)>>;