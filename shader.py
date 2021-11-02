import copy

rnd = lambda n: 3*round(n/3) + 1

class Shader():
    def __init__(self):
        self.dropoff = 35
        self.diagonaldropoff = round(self.dropoff * 1.4)
        self.upscale = False
        

    def set_dimensions(self, level):
        """Sets default empty shader arrays and attributes
        based on level passed. Should be called on every load
        and reload to avoid shadows breaking.
        """
        self.arrayx = level.width
        self.arrayy = level.height
        self.transparency_map = level.transparency_map
        self.baselighting, preprocesslights = level.generate_base_lighting()
        for light in preprocesslights:
            self.recurse(light, self.baselighting)
        self.empty_scaled_array = []
        for i in range(3 * self.arrayy):
            self.empty_scaled_array.append([])
            for j in range(3 * self.arrayx):
                self.empty_scaled_array[i].append(None)
        ...

    def recurse(self, light, array):
        """Recurses a light vector3 into adjacent tiles if possible."""
        if light[0] <= 0:
            return
        if array[light[2]][light[1]] > light[0]:
            return
        array[light[2]][light[1]] = light[0]
        if not self.transparency_map[light[2]][light[1]]:
            return
        if light[0] - self.dropoff > 0:
            if light[1] > 0:
                self.recurse([light[0] - self.dropoff, light[1] - 1, light[2]], array)
            if light[1] < self.arrayx - 1:
                self.recurse([light[0] - self.dropoff, light[1] + 1, light[2]], array)
            if light[2] > 0:
                self.recurse([light[0] - self.dropoff, light[1], light[2] - 1], array)
            if light[2] < self.arrayy - 1:
                self.recurse([light[0] - self.dropoff, light[1], light[2] + 1], array)
        if light[0] - self.diagonaldropoff > 0:
            if light[1] > 0 and light[2] > 0:
                self.recurse([light[0] - self.diagonaldropoff, light[1] - 1, light[2] - 1], array)
            if light[1] < self.arrayx - 1 and light[2] < self.arrayy - 1:
                self.recurse([light[0] - self.diagonaldropoff, light[1] + 1, light[2] + 1], array)
            if light[1] > 0 and light[2] < self.arrayy - 1:
                self.recurse([light[0] - self.diagonaldropoff, light[1] - 1, light[2] + 1], array)
            if light[1] < self.arrayx - 1 and light[2] > 0:
                self.recurse([light[0] - self.diagonaldropoff, light[1] + 1, light[2] - 1], array)
        return

    def generate_shadow_array(self, lightlist) -> "2D Array":
        """Pass a list of vector3s in the format
        [lightintensity, lightx, lighty] to
        return a 2d array of alpha values.
        """
        array = [x[:] for x in self.baselighting]
        # copying an array with [:] is significantly faster than copy.deepcopy()
        for light in lightlist:
            self.recurse(light, array)
        if self.upscale == True:
            array = self.upscalearray(array)
        return array
    
    def upscalearray(self, array) -> "2D Array":
        """Upscales a shadowmap array by 3 in each dimension
        and attempts to smoothen the values by applying
        bilinear interpolation. This method works fine, in theory,
        and the rendering is the problem.
        """
        output = [x[:] for x in self.empty_scaled_array]
        for i in range(self.arrayy):
            for j in range(self.arrayx):
                output[i * 3 + 1][j * 3 + 1] = array[i][j]
        ...
        for i in range(self.arrayy * 3):
            for j in range(self.arrayx * 3):
                if output[i][j] == None:
                    snapi = rnd(i)
                    if snapi > self.arrayy * 3:
                        snapi -= 3
                    elif snapi < 0:
                        snapi += 3
                    remj = j % 3
                    if 1 < j < self.arrayx * 3 - 2:
                        if remj == 0:
                            output[i][j] = int((output[snapi][j + 1] * 2 + output[snapi][j - 2]) / 3)
                        elif remj == 1:
                            output[i][j] = output[snapi][j]
                        elif remj == 2:
                            output[i][j] = int((output[snapi][j - 1] * 2 + output[snapi][j + 2]) / 3)
        return output