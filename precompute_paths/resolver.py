

# base class for all collision resolvers
class Resolver:


    def resolve_collision(self, flightpaths, collisions):
        pass
    
class ResolverDive(Resolver):
    # strategy: maintain original positions and directions, just alter altitude to dive beneath other planes
    def resolve_collision(self, flightpaths, collisions):
        
        # until all collisions are resolved:
        while len(collisions) > 0:
        # TODO
        #     resolve first collision
        #        change flight path
        #        update commands
        #     update collisions
            pass
        return False
    
class ResolverBruteForce(Resolver):
    def resolve_collision(self, flightpaths, collisions):
        return False