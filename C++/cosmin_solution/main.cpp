#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
#include <set>





class State
{
    uint16_t moves;
    std::map<uint32_t, std::set<uint32_t>> links;

    static std::map<char, uint8_t> color_registry;
    static uint8_t color_counter;

public:
    State()
    {
        
    }

    State(State& other)
    {
        moves = other.moves;
        links = other.links;
    }

    ~State()
    {

    }

    uint32_t combine(uint8_t color, uint16_t id)
    {
        uint32_t result;
        result = color;
        result = (result << 16) | id;
        return result;
    }

    void addLink(char color_a, uint16_t id_a, char color_b, uint16_t id_b)
    {
        if(color_registry.find(color_a) == color_registry.end())
        {
            color_registry[color_a] = color_counter;
            color_counter++;
        }

        if(color_registry.find(color_b) == color_registry.end())
        {
            color_registry[color_b] = color_counter;
            color_counter++;
        }

        uint32_t code_a = combine(color_registry[color_a], id_a);
        uint32_t code_b = combine(color_registry[color_b], id_b);
        links[code_a].insert(code_b);
        links[code_b].insert(code_a);
    }
    
    static uint8_t extractColor(uint32_t zone)
    {
        return (zone >> 16);
    }

    static uint16_t extractId(uint32_t zone)
    {
        return (zone & 0xFFFF);
    }

    void print_links()
    {
        for( auto const& [key, val] : links )
        {
            std::cout<< (key >> 16)<<" "<<(key & 0xFFFF) << ':' << std::endl ;

            std::set<uint32_t>::iterator it;

            for(it = val.begin(); it != val.end(); ++it)
            {
                std::cout<<((*it) >>16)<<" "<<((*it) & 0xFFFF)<<"; ";
            }
            std::cout<<std::endl;
        }
        
    }

    void replaceColor()

    uint8_t count_colors()
    {
        std::set<uint32_t> counter;
        for( auto const& [key, val] : links )
         {
             counter.insert(extractColor(key));
         }
         return counter.size();
    }

    std::vector<State> getNextStates()
    {
         for( auto const& [key, val] : links )
         {
             State tmpState = *this;


         }
    }

    bool is_complete()
    {
        uint8_t refColor = 0xFF;
        for( auto const& [key, val] : links )
        {
            if(refColor == 0xFF)
            {
                refColor = extractColor(key);
            }
            else
            {
                if(refColor != extractColor(key))
                    return false;
            }
        }
        return true;
    }

};

uint8_t State::color_counter = 0;
std::map<char, uint8_t> State::color_registry;

int main()
{
    State initial_state;
    initial_state.addLink('b', 0, 'r', 0);
    initial_state.addLink('r', 0, 'y', 0);
    initial_state.addLink('r', 0, 'b', 1);
    initial_state.addLink('r', 0, 'y', 1);

    initial_state.addLink('y', 0, 'b', 1);
    initial_state.addLink('b', 1, 'y', 1);
    initial_state.addLink('y', 0, 'r', 1);

    initial_state.addLink('r', 1, 'b', 1);
    initial_state.addLink('r', 1, 'y', 1);
    initial_state.addLink('r', 1, 'b', 2);

    std::cout<<"Count colors: "<<(int)initial_state.count_colors()<<std::endl;
    

    initial_state.print_links();

    return 0;
}