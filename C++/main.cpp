#include <iostream>
#include <vector>
#include <map>
#include <regex>

using namespace std;

string values[] =
{
	"Blue1 - Red1",
	"Yellow1 - Blue1",
	"Yellow2 - Red1",
	"Yellow2 - Blue1",
	"Red2 - Blue1",
	"Red2 - Yellow2",
	"Red2 - Yellow1",
	"Blue2 - Red1",
	"Blue2 - Yellow2",
	"Blue3 - Yellow1",
	"Blue3 - Red2",
	"Blue3 - Yellow2",
	"Red3 - Yellow2",
	"Yellow3 - Red2",
	"Blue4 - Red2",
	"Blue5 - Yellow2",
	"Yellow4 - Blue3",
	"Red4 - Yellow2",
	"Red4 - Blue3",
	"Red4 - Blue5"
};

string values1[] = 
{
	"Red1 - Blue1",
	"Blue2 - Red1",
	"Yellow1 - Blue2",
	"Blue3 - Yellow1"
};

string values2[] =
{
	"Blue1 - Green1",
	"Green2 - Blue1",
	"Blue2 - Green2",
	"Green3 - Blue2",
	"Green4 - Blue2",
	"Red1 - Blue1",
	"Red1 - Green1",
	"Red1 - Blue2",
	"Blue3 - Green1",
	"Blue3 - Red1",
	"Green5 - Blue2",
	"Green5 - Blue3",
	"Red2 - Blue2",
	"Green6 - Blue2",
	"Green6 - Blue3",
	"Red3 - Blue3",
	"Green7 - Blue3",
	"Red4 - Blue3",
	"Green8 - Blue3",
	"Green8 - Red4",
	"Green9 - Blue3",
	"Green10 - Red4",
	"Green10 - Blue3"
};

struct Node
{
	string name;
	string tag;
	vector<Node*> children;
	int weight = 0;
};

map<string, Node*> tags2Nodes;

bool is_only_one()
{
	int count = 0;
	std::string key;
	for (const auto & pair : tags2Nodes)
	{
		if (key.empty())
		{
			key = pair.second->name;
		}
		else
		{
			if (pair.second->name != key)
			{
				return false;
			}
		}
	}

	return true;
}

int main()
{
	for (string entry : values2)
	{
		std::regex r("(\\w+)(\\d+)\\s-\\s(\\w+)(\\d+)");
		std::smatch m;
		std::regex_search(entry, m, r);

		string fName = m[1].str();
		string fTag = m[1].str() + m[2].str();

		string sName = m[3].str();
		string sTag = m[3].str() + m[4].str();

		Node *first, *second;

		if (tags2Nodes.find(fTag) == tags2Nodes.end())
		{
			first = new Node();
			first->name = fName;
			first->tag = fTag;
			tags2Nodes.insert(std::pair<string, Node*>(fTag, first));
		}
		else
		{
			first = tags2Nodes.find(fTag)->second;
		}

		if (tags2Nodes.find(sTag) == tags2Nodes.end())
		{
			second = new Node();
			second->name = sName;
			second->tag = sTag;
			tags2Nodes.insert(std::pair<string, Node*>(sTag, second));
		}
		else
		{
			second = tags2Nodes.find(sTag)->second;
		}

		if(std::find(first->children.begin(), first->children.end(), second) == first->children.end())
			first->children.push_back(second);
		if (std::find(second->children.begin(), second->children.end(), first) == second->children.end())
			second->children.push_back(first);
	}

	while (!is_only_one())
	{
		/*for (const auto & pair : tags2Nodes)
		{
			std::cout << "(" << pair.second->name << ", " << pair.second->tag << ": ";
			for (int i = 0; i < (int)pair.second->children.size() - 1; ++i)
			{
				std::cout << "(" << pair.second->children[i]->name << ", " << pair.second->children[i]->tag << "), ";
			}
			if ((int)pair.second->children.size() - 1 >= 0)
			{
				std::cout << "(" << pair.second->children[pair.second->children.size() - 1]->name << ", " << pair.second->children[pair.second->children.size() - 1]->tag << ")" << std::endl;
			}
		}*/

		for (auto& node : tags2Nodes)
		{
			node.second->weight = 0;
		}

		// Go over every node and assign a note
		for (auto& node : tags2Nodes)
		{
			map<string, int> prio;
			for (auto& n : node.second->children)
			{
				prio[n->name] += 1;
			}

			int chance = 0;
			string tag = "";
			for (auto& p : prio)
				if (p.second > chance)
				{
					chance = p.second;
					tag = p.first;
				}
			node.second->weight = chance;
		}

		Node* currentNode = nullptr;
		for (auto& node : tags2Nodes)
		{
			if (currentNode == nullptr) currentNode = node.second;
			else if (node.second->weight > currentNode->weight)
				currentNode = node.second;
		}

		map<string, int> prio;
		for (auto& n : currentNode->children)
		{
			prio[n->name] += n->weight;
		}
		int chance = 0;
		string tag = "";
		for (auto& p : prio)
		{
			if (p.second > chance)
			{
				chance = p.second;
				tag = p.first;
			}
		}
		cout << "We need to eliminated node tagged " << currentNode->tag << " by converting to " << tag << endl;

		vector<Node*> children;
		for (auto& child : currentNode->children)
		{
			if (child->name == tag)
			{
				children.push_back(child);
			}
		}

		for (auto& child : children)
		{
			for (auto& relativ : child->children)
			{
				//if (find(relativ->children.begin(), relativ->children.end(), child) != relativ->children.end())
				relativ->children.erase(find(relativ->children.begin(), relativ->children.end(), child));
			}
			for (auto& relativ : child->children)
			{
				if (relativ == currentNode) continue;
				if (std::find(currentNode->children.begin(), currentNode->children.end(), relativ) == currentNode->children.end())
				{
					currentNode->children.push_back(relativ);
					relativ->children.push_back(currentNode);
				}
			}
			tags2Nodes.erase(child->tag);
		}

		currentNode->name = tag;
	}

	return 0;
}