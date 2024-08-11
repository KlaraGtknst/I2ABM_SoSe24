from unittest import TestCase, mock, main
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import math

from fire_evacuation.model import FireEvacuation
from fire_evacuation.agent import Human, Facilitator

INIT_NERVOUSNESS = 0.0  # avoid magic numbers

class AgentTest(TestCase):
    
    def setUp(self) -> None:

        # model
        self.model = FireEvacuation(floor_size = 14,
            human_count = 5,
            alarm_believers_prop = 1.0,
            max_speed = 2
            )

        # agent
        self.agent = Human(
                unique_id = 14*14,  # make sure it is unique
                speed = 2,
                orientation = Human.Orientation.NORTH,
                nervousness = INIT_NERVOUSNESS,
                cooperativeness = 0.8,
                believes_alarm = True,
                model = self.model,
                memory = None,
                memorysize = 0,
                turnwhenblocked_prop = 0.2,
                maxsight = math.inf,
                interactionmatrix = None,
        )
        self.model.grid.place_agent(self.agent, (3,3))


    def test_update_nervousness(self):
        # first test: few people at initialization -> no anxiety
        assert self.agent.nervousness == INIT_NERVOUSNESS
        
        # second test: many people -> anxiety
        # get positions of the neighborhood
        neighborhood = self.model.grid.get_neighborhood(self.agent.pos, moore=True,
                radius = self.agent.crowdradius) 
        # add people to the neighborhood
        people = []
        for i in range(1 + int(0.8 * len(neighborhood))):
            person = Human(
                unique_id = i,
                speed = 1,
                orientation = Human.Orientation.NORTH,
                nervousness = 0.7,
                cooperativeness = 0.8,
                believes_alarm = False,
                model = self.model,
                memory = None,
                memorysize = 0,
                turnwhenblocked_prop = 0.2,
                maxsight = math.inf,
                interactionmatrix = None,
            )
            people.append(person)
            self.model.grid.place_agent(person, neighborhood[i])
        self.agent.update_nervousness()
        assert self.agent.nervousness == INIT_NERVOUSNESS + Human.CROWD_ANXIETY_INCREASE , "nervousness: " + str(self.agent.nervousness)

         # third test: people leave -> few people -> no anxiety
        for i in range(1 + int(0.8 * len(neighborhood))):
            self.model.grid.remove_agent(people[i])
        self.agent.update_nervousness()
        assert self.agent.nervousness == INIT_NERVOUSNESS + Human.CROWD_ANXIETY_INCREASE - Human.CROWD_RELAXATION_DECREASE, "nervousness: " + str(self.agent.nervousness)
       
     
