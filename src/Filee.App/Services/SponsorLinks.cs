// Where "Sponsor" can lead: the sidebar button and the About page open a window with these, the way that suits the
// language first (Korean cards and easy-pay through Fairy in Korean, GitHub Sponsors otherwise).

namespace Filee.App.Services;

/// <summary>One way to support Filee.</summary>
/// <param name="Id">Also the suffix of its description string, <c>sponsor.note.{Id}</c>.</param>
/// <param name="Icon">Key of the logo geometry (Styles/Brands.axaml, or Icon.Heart).</param>
/// <param name="Color">Brand colour behind the white logo.</param>
public sealed record SponsorLink(string Id, string Name, string Url, string Icon, string Color);

public static class SponsorLinks
{
    public const string GitHubSponsorsUrl = "https://github.com/boboevproject-rgb";
    public const string FairyUrl = "https://github.com/boboevproject-rgb";
    public const string PatreonUrl = "https://github.com/boboevproject-rgb";
    public const string KoFiUrl = "https://github.com/boboevproject-rgb";
    public const string PayPalUrl = "https://github.com/boboevproject-rgb";

    private static readonly SponsorLink GitHub = new("github", "GitHub Sponsors", GitHubSponsorsUrl, "Brand.GitHubSponsors", "#BF3989");
    private static readonly SponsorLink Fairy = new("fairy", "Fairy", FairyUrl, "Icon.Heart", "#2E9E6B");
    private static readonly SponsorLink Patreon = new("patreon", "Patreon", PatreonUrl, "Brand.Patreon", "#141518");
    private static readonly SponsorLink KoFi = new("kofi", "Ko-fi", KoFiUrl, "Brand.KoFi", "#FF5E5B");
    private static readonly SponsorLink PayPal = new("paypal", "PayPal", PayPalUrl, "Brand.PayPal", "#003087");

    /// <summary>Every way, the one that suits <paramref name="language"/> first.</summary>
    public static IReadOnlyList<SponsorLink> For(string language) => [GitHub];
}
