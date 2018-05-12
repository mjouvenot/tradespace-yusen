import csv
import yaml
import utility_curves


class TradeSpace:
    def __init__(self, attributes, costs, design_decisions):
        self.attributes = attributes
        self.costs = costs
        self.impact_scores = {key: 0 for key in self.attributes.keys()}
        self.impact_scores.update({key: 0 for key in self.costs.keys()})
        self.design_decisions = design_decisions
        self.normalize(design_decisions)

    def normalize(self, design_decisions):
        #collect all the weights related to "affects" and normalize them to make a 0-1 scale
        for design_decision in design_decisions.values():
            for name, score in design_decision.affected_attributes.items():
                self.impact_scores[name] += score

    def generate_morph_matrix(self, file_name):
        with open(file_name, "w") as output_file:
            for name, design_decision in self.design_decisions.items():
                row = name + ","
                row += ",".join([option for option in design_decision.design_options.keys()])
                row += "\n"
                output_file.write(row)

    def score_concept(self, concept):
        assert isinstance(concept, dict)
        result = {}

        #Score attributes individually
        for attribute in self.impact_scores:
            score = 0
            for design_decision, option in concept.items():
                score += self.design_decisions[design_decision].score_option(attribute, option)
            result[attribute] = score/self.impact_scores[attribute]

        #Aggregate attributes score (weighted average)
        score = 0
        weights_total = 0
        for attr_name, attribute in self.attributes.items():
            score += attribute.utility_score(result[attr_name]) * attribute.weight
            weights_total += attribute.weight
        result['Utility'] = score/weights_total

        #Aggreagate cost score (weighted average)
        score = 0
        weights_total = 0
        for cost_name, cost in self.costs.items():
            score += result[cost_name] * cost.weight
            weights_total += cost.weight
        result['Cost'] = score/weights_total

        return result

    def __repr__(self):
        return "%s(attributes=%s, costs=%s, impact_scores=%s, design_decisions=%s)" % \
               (self.__class__.__name__,
                str(self.attributes), str(self.costs), str(self.impact_scores), str(self.design_decisions))

    def __str__(self):
        return self.__repr__()


class DesignDecision:
    rating = ['low', 'medium', 'high']
    def __init__(self, affected_attributes, options):
        attribute_names = []

        assert isinstance(affected_attributes, list)
        self.affected_attributes = {}
        for attribute in affected_attributes:
            assert len(attribute) == 1
            name = list(attribute.keys())[0]
            attribute_names.append(name)
            self.affected_attributes[name] = attribute[name]

        assert isinstance(options, list)
        self.design_options = {}
        for option in options:
            assert len(option) == 1
            name = list(option.keys())[0]
            assert len(option[name]) == len(affected_attributes)
            self.design_options[name] = {attribute_names[i]: option[name][i] for i in range(len(attribute_names))}

    def score_option(self, attribute, option):
        result = 0
        assert option in self.design_options
        if attribute in self.affected_attributes:
            coefficient = self.affected_attributes[attribute]
            qualitative_score = self.design_options[option][attribute]
            quantitative_score = self.rating.index(qualitative_score)/len(self.rating)
            result = quantitative_score * coefficient

        return result

    def __repr__(self):
        return "%s(affected_attributes=%s, design_options=%s)" % \
               (self.__class__.__name__,
                self.affected_attributes,
                self.design_options)

    def __str__(self):
        return self.__repr__()


class CostElement:
    def __init__(self, weight):
        assert isinstance(weight, int)
        self.weight = weight

    def _repr_(self):
        return "%s(weight=%s)" % \
               (self.__class__.__name__,
                self.weight)

    def __str__(self):
        return self._repr_()


class Attribute:
    def __init__(self, weight, utility, utility_params):
        assert isinstance(weight, int)
        assert isinstance(utility, str)
        assert isinstance(utility_params, dict)
        self.weight = weight
        self.utility = getattr(utility_curves, utility)
        self.utility_params = utility_params

    def utility_score(self, x):
        return self.utility(x, **self.utility_params)

    def _repr_(self):
        return "%s(weight=%s, utility=%s, utility_params=%s)" % \
               (self.__class__.__name__,
                self.weight,
                self.utility,
                self.utility_params)

    def __str__(self):
        return self._repr_()


def load_tradespace(file_name):
    attributes = {}
    costs = {}
    design_decisions = {}
    with open(file_name) as attributes_file:
        attributes_doc = yaml.load(attributes_file)
        for attribute in attributes_doc['attributes']:
            attributes[attribute['name']] = Attribute(**attribute['params'])

        for cost_element in attributes_doc['costs']:
            costs[cost_element['name']] = CostElement(**cost_element['params'])

        for design_decision in attributes_doc['design_decisions']:
            design_decisions[design_decision['name']] = DesignDecision(affected_attributes=design_decision['affects'],
                                                                       options=design_decision['options'])

    return TradeSpace(attributes=attributes, costs=costs, design_decisions=design_decisions)