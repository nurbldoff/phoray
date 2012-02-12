import matplotlib as mpl
import matplotlib.pyplot as plt
from math import asin, degrees
from phoray import Ray

def project_xz(raylist, final_length=0):
    pts=[]
    for rays in raylist:
        if not None in rays:
            element = []
            for r in rays:
                element.append((r.endpoint.x, r.endpoint.z, r.wavelength))
            # element.append((rays[-1].endpoint.x+10*rays[-1].direction.x,
            #                     rays[-1].endpoint.z+10*rays[-1].direction.z))
            if final_length:
                p = (rays[-1].endpoint + final_length * rays[-1].direction)
                element.append((p.x, p.z, rays[-1].wavelength))
                pts.append(element)
    return pts

def project_yz(raylist):
    pts=[]
    for rays in raylist:
        if not None in rays:

            element = []
            for r in rays:
                element.append((r.endpoint.y, r.endpoint.z, r.wavelength))
            # element.append((rays[-1].endpoint.z+10*rays[-1].direction.z,
            #                     rays[-1].endpoint.y+10*rays[-1].direction.y))
            pts.append(element)
    return pts

def project_xy(raylist):
    pts=[]
    for rays in raylist:
        if not None in rays:

            element = []
            for r in rays:
                element.append((r.endpoint.x, r.endpoint.y, r.wavelength))
            # element.append((rays[-1].endpoint.z+10*rays[-1].direction.z,
            #                     rays[-1].endpoint.y+10*rays[-1].direction.y))
            pts.append(element)
    return pts




def reflection_angle(ray1, ray2):
    return degrees(asin(ray1.direction.scalar(ray2.direction)))

def draw_projection(proj, mirror):
    fig = plt.figure()
    ax=fig.add_subplot(111)

    xmin=ymin=xmax=ymax=0
    #sm = mpl.cm.ScalarMappable(cmap=cm.jet_r)

    sm = mpl.cm.ScalarMappable(cmap=mpl.cm.jet_r)
    sm.set_clim(proj[-1][0][2], proj[0][0][2])

    for r in proj:
        ax.plot(r.T[0], r.T[1], zorder=1, c=sm.to_rgba(r[0][2]))
        xmin = min(xmin, min(r.T[0]))
        xmax=max(xmax, max(r.T[0]))
        ymin = min(ymin, min(r.T[1]))
        ymax=max(ymax, max(r.T[1]))

    xmargin = (xmax - xmin)*0.1
    ymargin = (ymax - ymin)*0.1
    ax.set_xlim(xmin-xmargin, xmax+xmargin)
    ax.set_ylim(ymin-ymargin, ymax+ymargin)
    #self.fig.show()
    #if filename is not None:
    #    self.fig.savefig(filename)

    # Nedanstaende funkar ej, missar rotationen av spegeln... bokigt.
    # grating_circle = plt.matplotlib.patches.Circle((
    #         (mirror.position.x-mirror.surface_offset.x),
    #         mirror.position.z-mirror.surface_offset.z), mirror.surface.R,
    #                                                fill=False, color="red", lw=0.25)
    # ax.add_patch(grating_circle)


def draw(self, filename=None):
    fig=plt.figure()


    # grating_circle = plt.matplotlib.patches.Arc((0, self.R_gr), 2*self.R_gr, 2*self.R_gr,
    #                                             angle=-90,
    #                                             theta1=-self.theta_in*180/pi,
    #                                             theta2=self.theta_in*180/pi,
    #                                             color="blue", lw=0.25)
    grating_circle = plt.matplotlib.patches.Circle((0, R), R,
                                                   fill=False, color="red", lw=0.25)
    ax.add_patch(grating_circle)

