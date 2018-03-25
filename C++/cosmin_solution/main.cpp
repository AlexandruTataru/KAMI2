#include <iostream>
#include <vector>
#include <algorithm>

typedef std::pair<unsigned int, unsigned int> Link;

typedef struct State
{
    std::vector<Link> links;
    unsigned char moves;
} State;

bool comparator(Link a, Link b)
{
    return (a.first < b.first);
}

bool checkColor(Link link, Link colorMock)
{
    return ((link.first & 0xFF00) < colorMock.first);
}

bool hasColor(State &s, unsigned int color)
{
    Link mock;
    mock.first = (color<<16);
    return std::binary_search(s.links.begin(), s.links.end(), mock, checkColor);
}

std::vector<State> expandState(std::vector<unsigned int>& colors, State& s)
{
    
}

bool isFinalState(State& s)
{
    return (s.links.empty());
}

int main()
{
    State s;

    std::vector<unsigned int> colors;

    std::sort(s.links.begin(), s.links.end(), comparator);

    return 0;
}


