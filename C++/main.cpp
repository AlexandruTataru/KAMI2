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

struct Node
{
	string name;
	string tag;
	vector<Node*> children;
	int weight = 0;
	string childTag2Remove;
};

map<string, Node*> tags2Nodes;

int main()
{
	for (string entry : values)
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

	while (!tags2Nodes.empty())
	{
		for (const auto & pair : tags2Nodes)
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
		}

		for (auto& node : tags2Nodes)
		{
			node.second->weight = 0;
			node.second->childTag2Remove = "";
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

		Node* toBeRemoved = nullptr;
		for (auto& node : tags2Nodes)
		{
			if (toBeRemoved == nullptr) toBeRemoved = node.second;
			else if (node.second->weight > toBeRemoved->weight)
				toBeRemoved = node.second;
		}

		map<string, int> prio;
		for (auto& n : toBeRemoved->children)
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
		toBeRemoved->childTag2Remove = tag;
		cout << "We need to eliminated node tagged " << toBeRemoved->tag << " by converting to " << tag << endl;

		vector<Node*> childrenToAdopt;
		for (auto& node : toBeRemoved->children)
		{
			if (node->name == toBeRemoved->childTag2Remove)
			{
				for (auto& childOfChild : node->children)
				{
					if (std::find(toBeRemoved->children.begin(), toBeRemoved->children.end(), childOfChild) == toBeRemoved->children.end())
						childrenToAdopt.push_back(childOfChild);
					if (std::find(childOfChild->children.begin(), childOfChild->children.end(), toBeRemoved) == childOfChild->children.end() && childOfChild != toBeRemoved)
						childOfChild->children.push_back(toBeRemoved);
					//childOfChild->children.erase(std::find(childOfChild->children.begin(), childOfChild->children.end(), node));
				}

				for (auto& taggedNodes : tags2Nodes)
				{
					if (taggedNodes.second == toBeRemoved) continue;
					if (std::find(taggedNodes.second->children.begin(), taggedNodes.second->children.end(), node) != taggedNodes.second->children.end())
					{
						taggedNodes.second->children.erase(std::find(taggedNodes.second->children.begin(), taggedNodes.second->children.end(), node));
					}
				}

				tags2Nodes.erase(node->tag);
			}
		}
		toBeRemoved->children.insert(toBeRemoved->children.end(), childrenToAdopt.begin(), childrenToAdopt.end());
		//cout << "We shall convert " << toBeRemoved->tag << " to " << toBeRemoved->childTag2Remove << endl;
		toBeRemoved->name = toBeRemoved->childTag2Remove;
	}

	return 0;
}