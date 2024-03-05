import numpy as np

class TimeSeriesSegments:
    """
    Class to support dividing time series into segments, each of which can have separately defined uncertainty parameters.
    If the series begins with a series of zeros, the uncertainty of this segment is assumed to be 0 (no uncertainty info needs 
    to be provided). The time series are handled using lists.
    """
    def __init__(self, x=None, y=None,  seg_delim=None, y_name=None):
        """
        Construct a new 'TimeSeriesSegments' object.
        :param x: The x-component of the time series (e.g. time)
        :param y: The y-component of the time series (e.g. values in time)
        :param seg_delim: Segment delimiters, i.e., the x-values at which a change in trend occurs
        """
        if x is None:
            raise ValueError('You must provide the x-component of the time series')
        elif type(x) != list:
            raise TypeError('The x-component of the time series must be a list')
        if y is None:
            raise ValueError('You must provide the y-component of the time series')
        elif type(y) != list:
            raise TypeError('The y-component of the time series must be a list')
        if seg_delim is None:
            raise ValueError('You must provide the segment delimiters variable')
        elif type(seg_delim) != list:
            raise TypeError('The segment delimiters variable must be a list')
        if y_name is None:
            y_name = 'y'
        assert (len(x) == len(y)), 'The x- and y-components need to have the same length'
        assert (type(x) == type(y) == list), 'Both x and y have to be lists'
        self.x = x
        self.y = y
        self.seg_delim = self.__create_segments__(seg_delim)
        self.no_of_segments = len(self.seg_delim)-1
        self.y_name = y_name
        if self.zeros_segment is True:
            self.no_of_nonzero_segments = self.no_of_segments-1
        else:
            self.no_of_nonzero_segments = self.no_of_segments

    def __get_segment_indices__(self):
        """
        Get indices to divide the data into segments
        :return: The indices
        """
        indices = []
        for s in range(0,self.no_of_segments):
            indices_for_s = []
            indices_for_s.append(self.x.index(self.seg_delim[s]))
            if s < self.no_of_segments -1:
                indices_for_s.append(self.x.index(self.seg_delim[s+1]))
            else:
                indices_for_s.append(self.x.index(self.seg_delim[s+1])+1)
            indices.append(indices_for_s)
        return indices

    def __create_segments__(self, seg_delim_manual):
        """
        Create segments based on provided trend seg_delim, which are supplemented by the first time series element, last element, and potentially the start of non-zero data
        :param seg_delim_manual: The manually defined values of x for which a change in trend occurs (=seg_delim)
        :return: The extended seg_delim (supplemented by 2 or 3 points)
        """
        self.zeros_segment = False # does the time series begin with a series of zeros? default: False
        seg_delim = []
        seg_delim += [self.x[0]] # first year of the data series
        first_nonzero  = list(ele > 0 for ele in self.y).index(True) # index of the first nonzero element
        if self.x[first_nonzero] != self.x[0]: # in case there is a series of zeros at the beginning, it becomes a segment of its own, with zero uncertainty
            seg_delim += [self.x[first_nonzero]]
            self.zeros_segment = True
        seg_delim += seg_delim_manual
        seg_delim += [self.x[-1]] # last year of data series
        return seg_delim

    def add_shift(self, shift):
        y_segs = self.get_y_segments()
        shifted = []
        offset = 0
        if self.zeros_segment is True:
            shifted += y_segs[0] # add zero segment
            offset = 1
        if len(shift)!=self.no_of_nonzero_segments:
            raise ValueError('Mismatch in number of non-zero segments and length of the provided shift information.')
        for i in range(0, self.no_of_nonzero_segments):
            y_seg = y_segs[i+offset]
            shifted += list(np.array(y_seg)*(1+shift[i]))
        self.y = shifted
        return

    def get_x_segments(self): 
        """
        Get the x-vector divided by segments
        :return: The x-vector divided by segments
        """
        s_indices = self.__get_segment_indices__()
        x_segments = []
        for si in s_indices:
            x_segments.append(self.x[si[0]:si[1]])
        return x_segments

    def get_y_segments(self):
        """
        Get the y-vector divided by segments
        :return: The y-vector divided by segments
        """
        s_indices = self.__get_segment_indices__()
        y_segments = []
        for si in s_indices:
            y_segments.append(self.y[si[0]:si[1]])
        return y_segments
    
    def add_uncertainties(self, dist, par1, par2):
        """
        Add uncertainty for the non-zero time series segments. The uncertainty is defined using a list with standard deviation values, 
        as many as there are non-zero segments. We assume normal distribution. 
        :param stdev: List containing 'bounds' and 'dists' items
        """
        s_indices = self.__get_segment_indices__()
        if type(dist) == list:
            if len(dist)!=self.no_of_nonzero_segments:
                raise ValueError('Mismatch in number of non-zero segments and length of the provided uncertainty information.')
        elif type(dist) == str:
            dist = [dist]*self.no_of_nonzero_segments
        else:
            raise TypeError('Variable dist must be of type list or string')
        if type(par1) == list:
            if len(par1)!=self.no_of_nonzero_segments:
                raise ValueError('Mismatch in number of non-zero segments and length of the provided uncertainty information.')
        elif type(par1) in [float, int]:
            par1 = [par1]*self.no_of_nonzero_segments
        else:
            raise TypeError('Variable par1 must be of type list, float or int')
        if type(par2) == list:
            if len(par2)!=self.no_of_nonzero_segments:
                raise ValueError('Mismatch in number of non-zero segments and length of the provided uncertainty information.')
        elif type(par2) == float:
            par2 = [par2]*self.no_of_nonzero_segments
        else:
            raise TypeError('Variable par2 must be of type list or float')
        self.uncert = {}
        self.uncert['names'] = []
        self.uncert['dists'] = []
        self.uncert['bounds'] = []
        for i,si in enumerate(s_indices[1:]): # starts with the 2nd element to omit the zero segment
            self.uncert['names'].append(self.y_name+'-'+str(self.x[si[0]])+'-'+str(self.x[si[1]-1]))
            self.uncert['dists'].append(dist[i])
            self.uncert['bounds'].append([par1[i],par2[i]])
        return

    def get_stdevs(self,no_st_dev: int):
        """
        Get the upper and lower bounds, given the number of standard deviations
        :param no_st_dev: The number of standard deviations (e.g., 2)
        :return: List [l,u], where l is the lower bound and h is the upper bound
        """
        if not self.uncert:
            raise AttributeError(f'The uncertainty has not been added to the TimeSeriesSegments object')
        y_segs = self.get_y_segments()
        l = []
        u = []
        start = 0
        if self.zeros_segment is True:
            l += y_segs[0] # add zero segment
            u += y_segs[0] # add zero segment
            start = 1
        for i in range(start, len(y_segs)):
            bounds = self.uncert['bounds'][i-1]
            dist = self.uncert['dists'][i-1]
            y_seg = y_segs[i]
            if dist == "norm":
                # z = stats.norm.ppf((level+(100-level)/2)/100)
                l += list(np.array(y_seg) *(1-bounds[1]*no_st_dev))
                u += list(np.array(y_seg) *(1+bounds[1]*no_st_dev))
            else:
                raise ValueError(f'The distribution name "{dist}" is not known.')# the distribution is not known, confidence intervals cannot be computed
        return [l,u]
    
    def combine_segments(self, var_seg):
        """
        Combines segments into one variable
        :param var_seg: Variable segments (lists)
        :return: The variable combined back into one time series
        """
        var = []
        for seg in var_seg:
            var += seg
        return var
   
    def multiply_inflows_by_piecewise_uncert(self,*u_inflows):
        y_segs = self.get_y_segments()
        inflows = np.array([])
        offset = 0
        if all(v == 0 for v in y_segs[0]): # if the first segment is only zeros
            inflows = np.append(inflows, y_segs[0])
            offset = 1
        u_segs = [seg for seg in u_inflows[0]]
        for i in range(0,len(u_segs)):
            inflows = np.append(inflows, np.array(y_segs[i+offset])*(1+u_segs[i]))
        return inflows