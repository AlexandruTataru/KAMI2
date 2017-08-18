#include <iostream>
#include <vector>
#include <map>
#include <regex>

using namespace std;

string values[] =
{
	"LightBlue1 - DarkRed1",
	"PaperGrey1 - LightBlue1",
	"LightBlue2 - PaperGrey1",
	"DarkRed2 - LightBlue2",
	"PaperGrey2 - DarkRed1",
	"LightBlue3 - DarkRed1",
	"LightBlue4 - PaperGrey2"
};

struct Node
{
	string visibleColor;
	string hiddenTag;
	int simpleWeight;
	vector<Node*> neighbors;
};

map<string, Node*> tags2Nodes;

bool colorIsUniform()
{
	int count = 0;
	std::string key;
	for (const auto & pair : tags2Nodes)
	{
		if (key.empty())
			key = pair.second->visibleColor;
		else
			if (pair.second->visibleColor != key)
				return false;
	}
	return true;
}

void displayGraph()
{
	for (const auto & pair : tags2Nodes)
	{
		std::cout << "(" << pair.second->visibleColor << ", " << pair.second->hiddenTag << ": ";
		for (int i = 0; i < (int)pair.second->neighbors.size() - 1; ++i)
		{
			std::cout << "(" << pair.second->neighbors[i]->visibleColor << ", " << pair.second->neighbors[i]->hiddenTag << "), ";
		}
		if ((int)pair.second->neighbors.size() - 1 >= 0)
		{
			std::cout << "(" << pair.second->neighbors[pair.second->neighbors.size() - 1]->visibleColor << ", " << pair.second->neighbors[pair.second->neighbors.size() - 1]->hiddenTag << ")" << std::endl;
		}
	}
}

void readInputDataAndCreateGraph()
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
			first->visibleColor = fName;
			first->hiddenTag = fTag;
			tags2Nodes.insert(std::pair<string, Node*>(fTag, first));
		}
		else
		{
			first = tags2Nodes.find(fTag)->second;
		}

		if (tags2Nodes.find(sTag) == tags2Nodes.end())
		{
			second = new Node();
			second->visibleColor = sName;
			second->hiddenTag = sTag;
			tags2Nodes.insert(std::pair<string, Node*>(sTag, second));
		}
		else
		{
			second = tags2Nodes.find(sTag)->second;
		}

		if (std::find(first->neighbors.begin(), first->neighbors.end(), second) == first->neighbors.end())
			first->neighbors.push_back(second);
		if (std::find(second->neighbors.begin(), second->neighbors.end(), first) == second->neighbors.end())
			second->neighbors.push_back(first);
	}
}

void assignSimpleWeightToTheNodes()
{
	for (auto& node : tags2Nodes)
	{
		map<string, int> prio;
		for (auto& n : node.second->neighbors)
			prio[n->visibleColor] += 1;

		int weight = 0;
		for (auto& p : prio)
			if (p.second > weight)
				weight = p.second;
		node.second->simpleWeight = weight;
	}
}

Node* getMainNode()
{
	Node* currentNode = nullptr;
	int maxWeight = 0;
	for (auto& node : tags2Nodes)
	{
		map<string, int> prio;
		for (auto& n : node.second->neighbors)
		{
			prio[n->visibleColor] += n->simpleWeight;
		}

		int hiddenWeight = 0;
		for (auto& p : prio)
		{
			if (p.second > maxWeight)
			{
				maxWeight = p.second;
				currentNode = node.second;
			}
			else if (p.second == maxWeight)
			{
				if (node.second->simpleWeight > currentNode->simpleWeight)
				{
					currentNode = node.second;
				}
			}
		}
	}
	return currentNode;
}

string getNewColorForNode(const Node* currentNode)
{
	map<string, int> prio;
	for (auto& n : currentNode->neighbors)
	{
		prio[n->visibleColor] += n->simpleWeight;
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

	return tag;
}

void eraseNode(Node* currentNode, const string& tag)
{
	vector<Node*> children;
	for (auto& child : currentNode->neighbors)
	{
		if (child->visibleColor == tag)
		{
			children.push_back(child);
		}
	}

	for (auto& child : children)
	{
		for (auto& relativ : child->neighbors)
		{
			relativ->neighbors.erase(find(relativ->neighbors.begin(), relativ->neighbors.end(), child));
		}
		for (auto& relativ : child->neighbors)
		{
			if (relativ == currentNode) continue;
			if (std::find(currentNode->neighbors.begin(), currentNode->neighbors.end(), relativ) == currentNode->neighbors.end())
			{
				currentNode->neighbors.push_back(relativ);
				relativ->neighbors.push_back(currentNode);
			}
		}
		tags2Nodes.erase(child->hiddenTag);
	}
	currentNode->visibleColor = tag;
}

int main()
{
	readInputDataAndCreateGraph();
	while (!colorIsUniform())
	{
		for (auto& node : tags2Nodes)
			node.second->simpleWeight = 0;

		assignSimpleWeightToTheNodes();
		Node* currentNode = getMainNode();
		string newNodeColor = getNewColorForNode(currentNode);
		cout << "We need to eliminated node tagged " << currentNode->hiddenTag << " by converting to " << newNodeColor << endl;
		eraseNode(currentNode, newNodeColor);
	}

	return 0;
}